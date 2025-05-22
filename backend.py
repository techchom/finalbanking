# backend.py
import os
import sys

# ----------------------------------------
# Funksioni për logim të gabimeve
# ----------------------------------------
def log_error(tipi, pershkrimi, burimi):
    print(f"ERROR: {tipi} - {pershkrimi} - {burimi}")

# ----------------------------------------
# Leximi i llogarive nga current_accounts.txt
# ----------------------------------------
def lexo_master_accounts(path="data/current_accounts.txt"):
    accounts = {}
    try:
        with open(path, "r") as file:
            for line in file:
                line = line.strip()
                if "END_OF_FILE" in line:
                    break
                nr = line[0:5]
                emri = line[6:26].strip()
                status = line[27]
                balance = float(line[29:37])
                accounts[nr] = {
                    "name": emri,
                    "status": status,
                    "balance": balance,
                    "plan": "SP",
                    "count": 0
                }
        return accounts
    except Exception as e:
        log_error("Fatal Error", "Nuk mund të lexohet current_accounts.txt", path)
        sys.exit(1)

# ----------------------------------------
# Leximi i transaksioneve nga session_transactions.txt
# ----------------------------------------
def lexo_transaksionet(path="data/session_transactions.txt"):
    transaksionet = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    kodi = line[0:2]
                    if kodi == "00":
                        transaksionet.append({
                            "kodi": "00",
                            "emri": "",
                            "nr": "00000",
                            "shuma": 0.0,
                            "shtese": "00"
                        })
                        continue
                    emri = line[3:23].strip()
                    nr = line[24:29].strip()
                    shuma = float(line[30:38])
                    shtese = line[39:41].strip()
                    transaksionet.append({
                        "kodi": kodi,
                        "emri": emri,
                        "nr": nr,
                        "shuma": shuma,
                        "shtese": shtese
                    })
                except:
                    log_error("Fatal Error", "Format i gabuar i transaksionit", line)
                    sys.exit(1)
        return transaksionet
    except Exception:
        log_error("Fatal Error", "Nuk mund të hapet session_transactions.txt", path)
        sys.exit(1)

# ----------------------------------------
# Aplikimi i transaksioneve mbi accounts
# ----------------------------------------
def apliko_transaksione(accounts, transaksionet):
    for trans in transaksionet:
        kodi = trans["kodi"]
        emri = trans["emri"].strip()
        nr = trans["nr"].strip()
        shuma = trans["shuma"]
        shtese = trans["shtese"].strip()

        if kodi == "00":
            break

        def kosto(nr):
            return 0.05 if accounts[nr]["plan"] == "SP" else 0.10

        if kodi == "01":
            if nr in accounts and accounts[nr]["name"] == emri:
                totali = shuma + kosto(nr)
                if accounts[nr]["balance"] >= totali:
                    accounts[nr]["balance"] -= totali
                    accounts[nr]["count"] += 1
                else:
                    log_error("Failed Constraint", "Tërheqje me balancë negative", trans)
            else:
                log_error("Failed Constraint", "Llogaria nuk ekziston për withdrawal", trans)

        elif kodi == "02":
            nga = nr
            te = shtese
            if nga in accounts and te in accounts:
                totali = shuma + kosto(nga)
                if accounts[nga]["balance"] >= totali:
                    accounts[nga]["balance"] -= totali
                    accounts[te]["balance"] += shuma
                    accounts[nga]["count"] += 1
                else:
                    log_error("Failed Constraint", "Transfer me balancë negative", trans)
            else:
                log_error("Failed Constraint", "Një nga llogaritë nuk ekziston për transfer", trans)

        elif kodi == "03":
            if nr in accounts and accounts[nr]["name"] == emri:
                if shtese not in ["EC", "CQ", "FI"]:
                    log_error("Failed Constraint", "Kompania e pavlefshme për fature", trans)
                    continue
                totali = shuma + kosto(nr)
                if accounts[nr]["balance"] >= totali:
                    accounts[nr]["balance"] -= totali
                    accounts[nr]["count"] += 1
                else:
                    log_error("Failed Constraint", "Pagesë me balancë negative", trans)
            else:
                log_error("Failed Constraint", "Llogaria nuk ekziston për pagesë", trans)

        elif kodi == "04":
            if nr in accounts:
                accounts[nr]["balance"] += shuma
                accounts[nr]["balance"] -= kosto(nr)
                accounts[nr]["count"] += 1
            else:
                log_error("Failed Constraint", "Llogaria nuk ekziston për depozitë", trans)

        elif kodi == "05":
            if nr not in accounts:
                accounts[nr] = {
                    "name": emri,
                    "status": "A",
                    "balance": shuma,
                    "plan": "SP",
                    "count": 0
                }
            else:
                log_error("Failed Constraint", f"Llogaria {nr} tashmë ekziston - CREATE dështon", trans)

        elif kodi == "06":
            if nr in accounts and accounts[nr]["name"] == emri:
                del accounts[nr]
            else:
                log_error("Failed Constraint", "Llogaria nuk ekziston për fshirje", trans)

        elif kodi == "07":
            if nr in accounts and accounts[nr]["name"] == emri:
                accounts[nr]["status"] = "D"
            else:
                log_error("Failed Constraint", "Llogaria nuk ekziston për çaktivizim", trans)

        elif kodi == "08":
            if nr in accounts and accounts[nr]["name"] == emri:
                accounts[nr]["plan"] = shtese if shtese in ["SP", "NP"] else accounts[nr]["plan"]
            else:
                log_error("Failed Constraint", "Llogaria nuk ekziston për ndryshim plani", trans)

# ----------------------------------------
# Shkruan new_master_accounts.txt (me count)
# ----------------------------------------
def shkruaj_master(accounts, path="data/new_master_accounts.txt"):
    with open(path, "w") as f:
        for nr in sorted(accounts.keys()):
            acc = accounts[nr]
            line = f"{nr.zfill(5)}_{acc['name'].ljust(20)[:20]}_{acc['status']}_{acc['balance']:08.2f}_{str(acc['count']).zfill(4)}\n"
            f.write(line)

# ----------------------------------------
# Shkruan new_current_accounts.txt (pa count)
# ----------------------------------------
def shkruaj_current(accounts, path="data/new_current_accounts.txt"):
    with open(path, "w") as f:
        for nr in sorted(accounts.keys()):
            acc = accounts[nr]
            line = f"{nr.zfill(5)}_{acc['name'].ljust(20)[:20]}_{acc['status']}_{acc['balance']:08.2f}\n"
            f.write(line)
        f.write("00000_END_OF_FILE___________A_00000.00_\n")

# ---------------------------------------
# Funksioni kryesor
# ----------------------------------------
def main():
    accounts = lexo_master_accounts()
    transaksionet = lexo_transaksionet()
    apliko_transaksione(accounts, transaksionet)
    shkruaj_master(accounts)
    shkruaj_current(accounts)
    print("✅ Back End përfundoi me sukses.")

if __name__ == "__main__":
    main()

