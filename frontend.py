import os
import sys
import msvcrt
import csv
from datetime import datetime

pending_accounts = {}
pending_deposits = {}
accounts = {}
session = {
    "logged_in": False,
    "account_number": None,
    "user_name": None,
    "is_admin": False,
    "plan": "SP",
    "withdrawn_this_session": 0.0,
    "transferred_this_session": 0.0,  # NEW: track session transfer total
    "deposited_this_session": 0.0,  # NEW: track session deposit total
    "paidbills_this_session": 0.0,  # NEW: track session paybill total
}

withdrawn_today = 0.0
deposited_today = 0.0
transferred_today = 0.0
paidbills_today = 0.0

def ngjyros(text, fg="97;1", bg="104"):
    return f"\033[{fg};{bg}m{text}\033[0m"

def formo_transaksion(kodi, nr, shuma, shtese="00"):
    nr = nr.zfill(5)
    emri = session['user_name'].ljust(20)[:20]
    shuma = f"{float(shuma):08.2f}"
    shtese = shtese.ljust(2)[:2]
    return f"{kodi}_{emri}_{nr}_{shuma}_{shtese}"

def password_me_yje(prompt="Password: "):
    print(prompt, end='', flush=True)
    password = ""
    while True:
        char = msvcrt.getch()
        if char in [b'\r', b'\n']:
            print('')
            break
        elif char == b'\x08':
            if len(password) > 0:
                password = password[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        elif char == b'\x03':
            raise KeyboardInterrupt
        else:
            try:
                c = char.decode('utf-8')
                password += c
                sys.stdout.write('*')
                sys.stdout.flush()
            except:
                continue
    return password

def regjistro_csv(kodi, lloji, nga, shuma, shtese=""):
    with open("data/session_transactions.csv", "a", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        koha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([koha, kodi, lloji, nga, f"{shuma:.2f}", shtese])

def inicializo_csv_nqs_sduhet():
    path = "data/session_transactions.csv"
    if not os.path.exists(path):
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Koha", "Kodi", "Lloji", "Nga (emri)", "Shuma (€)", "Shtese"])

def ruaj_accounts():
    with open("data/current_accounts.txt", "w") as f:
        for nr, info in accounts.items():
            nr_f = nr.zfill(5)
            emri_f = info['name'].ljust(20)[:20]
            status_f = info['status']
            balanca_f = f"{float(info['balance']):08.2f}"
            line = f"{nr_f}_{emri_f}_{status_f}_{balanca_f}\n"
            f.write(line)
        # Rreshti i fundit për mbyllje
        f.write("00000_END_OF_FILE___________A_00000.00_\n")



def lexo_accounts():
    if not os.path.exists("data/current_accounts.txt"):
        print("❌ Skedari i llogarive nuk ekziston.")
        return False
    with open("data/current_accounts.txt", "r") as file:
        for line in file:
            line = line.strip()
            if "END_OF_FILE" in line:
                break
            nr = line[0:5]
            emri = line[6:26].strip()
            status = line[27]
            balance = float(line[29:37])
            password = line[38:].strip() if len(line) > 38 else "1234"
            accounts[nr] = {"name": emri, "status": status, "balance": balance, "password": password}
    return True


def login():
    if session['logged_in']:
        print("⚠️ Tashmë jeni të kyçur. Dilni para se të kyçeni përsëri.")
        return

    print(ngjyros("👤 Zgjidh llojin e përdoruesit:"))
    tipi = input("[standard/admin] > ").strip().lower()
    if tipi not in ["standard", "admin"]:
        print("❌ Lloj përdoruesi i pavlefshëm.")
        return

    username = input("👤 Emri i përdoruesit: ").strip()

    # Kontrollo menjëherë pas emrit
    if username.lower() == "admin" and tipi != "admin":
        print("❌ Llogaria Admin mund të kyçet vetëm si admin.")
        return
    if username.lower() != "admin" and tipi == "admin":
        print("❌ Vetëm llogaria Admin mund të kyçet si admin.")
        return

    password = password_me_yje("🔑 Fjalëkalimi: ")

    # --- Kontrolli i kërkuar ---
    # Gjej numrin e llogarisë për këtë emër përdoruesi
    nr_admin = None
    for nr, info in accounts.items():
        if info['name'] == username:
            nr_admin = nr
            break

    if nr_admin == "00000" and tipi != "admin":
        print("❌ Llogaria 00000 mund të kyçet vetëm si admin.")
        return
    if nr_admin != "00000" and tipi == "admin":
        print("❌ Vetëm llogaria 00000 mund të kyçet si admin.")
        return
    # --- Fund kontrolli ---

    for nr, info in accounts.items():
        if info['name'] == username and info.get('password') == password:
            if info['status'] == 'D':
                print("🚫 Llogaria është e çaktivizuar.")
                return
            # Këtu nuk duhet më kontrolli për admin sepse është bërë më lart
            session['logged_in'] = True
            session['account_number'] = nr
            session['user_name'] = info['name']
            session['is_admin'] = (tipi == "admin")
            session['withdrawn_this_session'] = 0.0  # reset on login
            session['transferred_this_session'] = 0.0  # reset on login
            session['deposited_this_session'] = 0.0  # reset on login
            session['paidbills_this_session'] = 0.0  # reset on login
            print(f"✅ U kyçët si {'administrator' if session['is_admin'] else 'përdorues standard'}: {session['user_name']}")
            print(f"💳 Balanca aktuale: {accounts[nr]['balance']:.2f}€")
            shfaq_komandat()
            return

    print("❌ Kyçja dështoi. Kontrolloni kredencialet.")
def shfaq_komandat():
    print(ngjyros("\n📘 Komandat në dispozicion:"))
    print("🔹 çkyçu – Çkyçu nga llogaria")  # changed from 'logout'
    print("🔹 dalje – Dil nga aplikacioni")
    print("🔹 bilanci – Shfaq balancën tënde aktuale")
    print("🔹 depozitë – Shto para në llogarinë tënde")
    print("🔹 tërheqje – Tërhiq para nga llogaria")
    print("🔹 transfero – Transfero para në një llogari tjetër")
    print("🔹 faturë – Paguaj një faturë (EC, CQ, FI)")
    print("🔹 ndryshofjalekalim – Ndrysho fjalëkalimin")
    print("🔹 historik – Shfaq historikun e transaksioneve")
    if session['is_admin']:
        print("🔸 krijo – Krijo llogari të re")
        print("🔸 fshijllogari – Fshij një llogari ekzistuese")
        print("🔸 çaktivizo – Çaktivizo një llogari")
        print("🔸 ndryshoplan – Ndrysho planin e një llogarie")
        print("🔸 bilancet – Shfaq balancat e të gjithë përdoruesve")

def logout():
    if not session['logged_in']:
        print("❌ Nuk jeni të kyçur.")
        return

    # Regjistro logout në historik
    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("00", "00000", "00000.00", "00") + "\n")

    # Aktivizo llogaritë e reja të krijuara gjatë këtij sesioni
    if pending_accounts:
        for nr, info in pending_accounts.items():
            accounts[nr] = info
        pending_accounts.clear()
        print("✅ Llogaritë e reja u aktivizuan pas logout-it.")

    # Apliko depozitat në pritje
    if pending_deposits:
        for nr, shuma in pending_deposits.items():
            if nr in accounts:
                accounts[nr]['balance'] += shuma
        pending_deposits.clear()
        print("✅ Depozitat në pritje u aplikuan pas logout-it.")

    # Ruaj gjendjen e fundit
    ruaj_accounts()

    # Reset sesionin
    session.update({
        "logged_in": False,
        "account_number": None,
        "user_name": None,
        "is_admin": False
    })
    session['withdrawn_this_session'] = 0.0  # reset on logout
    session['transferred_this_session'] = 0.0  # reset on logout
    session['deposited_this_session'] = 0.0  # reset on logout
    session['paidbills_this_session'] = 0.0  # reset on logout

    print("👋 U çkyçët me sukses.")


def shfaq_balancen_time():
    nr = session['account_number']
    balanca = accounts[nr]['balance']
    print(f"💳 Balanca jote aktuale: {balanca:.2f}€")

def shfaq_te_gjithe_balancat():
    if not session['is_admin']:
        print("❌ Vetëm administratori mund të shohë të gjitha balancat.")
        return
    print(ngjyros("\n💼 Lista e llogarive dhe balancave:"))
    for nr, info in accounts.items():
        status = "❌ (çaktivizuar)" if info['status'] == 'D' else ""
        print(f"🔹 {nr} – {info['name']} – {info['balance']:.2f}€ {status}")

def ndrysho_fjalekalim():
    nr = session['account_number']
    aktual = password_me_yje("🔐 Fjalëkalimi aktual: ")
    if accounts[nr]['password'] != aktual:
        print("❌ Fjalëkalimi i gabuar.")
        return
    ri = password_me_yje("🆕 Fjalëkalimi i ri: ")
    accounts[nr]['password'] = ri
    ruaj_accounts()
    print("✅ Fjalëkalimi u ndryshua me sukses.")

def shfaq_historik():
    if not os.path.exists("data/session_transactions.txt"):
        print("📂 Nuk ka historik transaksionesh.")
        return
    nr = session['account_number']
    print(ngjyros(f"\n📜 Historiku për llogarinë {nr}:"))
    with open("data/session_transactions.txt", "r") as f:
        for rresht in f:
            if nr in rresht:
                print(rresht.strip())

pending_deposits = {}

def depozite():
    global deposited_today
    if session['is_admin']:
        nr = input("🔢 Numri i llogarisë për depozitë: ").strip().zfill(5)
        emri = input("👤 Emri i mbajtësit të llogarisë: ").strip()
        if nr not in accounts or accounts[nr]['name'] != emri:
            print("❌ Llogaria nuk ekziston ose emri nuk përputhet.")
            return
    else:
        nr = session['account_number']

    shuma_input = input("💰 Shuma për depozitë: ").strip()
    try:
        shuma = float(shuma_input)
    except ValueError:
        print("❌ Shuma e pavlefshme.")
        return
    if shuma <= 0:
        print("❌ Shuma duhet të jetë më e madhe se 0.")
        return

    if not session['is_admin']:
        if deposited_today + shuma > 9999.99:
            print("🚫 Kufiri maksimal ditor për depozitë për përdorues standard është 9999.99€.")
            return
    pending_deposits[nr] = pending_deposits.get(nr, 0) + shuma

    if not session['is_admin']:
        deposited_today += shuma  # track daily deposit

    print(f"✅ {shuma:.2f}€ u pranua për depozitë në llogarinë {nr} (në pritje).")
    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("04", nr, shuma) + "\n")
    regjistro_csv("04", "Depozitë", accounts[nr]['name'], shuma)

def terheqje():
    global withdrawn_today
    if session['is_admin']:
        nr = input("🔢 Numri i llogarisë për tërheqje: ").strip().zfill(5)
        emri = input("👤 Emri i mbajtësit të llogarisë: ").strip()
        if nr not in accounts or accounts[nr]['name'] != emri:
            print("❌ Llogaria nuk ekziston ose emri nuk përputhet.")
            return
    else:
        nr = session['account_number']

    shuma = input("🏧 Shuma për tërheqje: ").strip()
    try:
        shuma = float(shuma)
    except ValueError:
        print("❌ Shuma e pavlefshme.")
        return
    if shuma <= 0:
        print("❌ Shuma duhet të jetë më e madhe se 0.")
        return
    if not session['is_admin']:
        if withdrawn_today + shuma > 500:
            print("🚫 Kufiri maksimal ditor për tërheqje për përdorues standard është 500€.")
            return
    if accounts[nr]['balance'] < shuma:
        print("🚫 Balanca e pamjaftueshme.")
        return

    accounts[nr]['balance'] -= shuma
    if not session['is_admin']:
        withdrawn_today += shuma  # track daily withdrawal
    print(f"✅ Tërhoqët {shuma:.2f}€ nga llogaria {nr}. Balanca e re: {accounts[nr]['balance']:.2f}€")
    
    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("01", nr, shuma) + "\n")
    regjistro_csv("01", "Tërheqje", accounts[nr]['name'], shuma)

def transfero():
    global transferred_today
    print("🔁 Fillimi i transferimit të mjeteve.")
    if session['is_admin']:
        from_nr = input("🔢 Numri i llogarisë burim: ").strip().zfill(5)
        emri = input("👤 Emri i mbajtësit të llogarisë: ").strip()
        if from_nr not in accounts or accounts[from_nr]['name'] != emri:
            print("❌ Llogaria burim nuk ekziston ose emri nuk përputhet.")
            return
    else:
        from_nr = session['account_number']

    to_nr = input("🔢 Numri i llogarisë përfitues: ").strip().zfill(5)
    if to_nr not in accounts:
        print("❌ Llogaria përfitues nuk ekziston.")
        return
    if accounts[to_nr]['status'] == 'D':
        print("🚫 Llogaria përfitues është e çaktivizuar.")
        return
    if from_nr == to_nr:
        print("❌ Nuk mund të transferoni në të njëjtën llogari.")
        return

    shuma = input("💸 Shuma për transferim: ").strip()
    try:
        shuma = float(shuma)
    except ValueError:
        print("❌ Shuma e pavlefshme.")
        return
    if shuma <= 0:
        print("❌ Shuma duhet të jetë më e madhe se 0.")
        return

    # Së pari kontrollo balancën
    if accounts[from_nr]['balance'] < shuma:
        print("🚫 Nuk keni fonde të mjaftueshme në llogari.")
        return

    # Pastaj kontrollo kufirin ditor për përdorues standard
    if not session['is_admin']:
        if transferred_today + shuma > 1000:
            print("🚫 Kufiri maksimal ditor për transfer për përdorues standard është 1000€.")
            return

    accounts[from_nr]['balance'] -= shuma
    accounts[to_nr]['balance'] += shuma

    if not session['is_admin']:
        transferred_today += shuma  # track daily transfer

    print(f"✅ {shuma:.2f}€ u transferuan nga {from_nr} ({accounts[from_nr]['name']}) te {to_nr} ({accounts[to_nr]['name']}).")
    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("02", from_nr, shuma, to_nr) + "\n")
    regjistro_csv("02", "Transfer", accounts[from_nr]['name'], shuma, to_nr)

def paguaj_fature():
    global paidbills_today
    if session['is_admin']:
        nr = input("🔢 Numri i llogarisë për pagesë: ").strip().zfill(5)
        emri = input("👤 Emri i mbajtësit të llogarisë: ").strip()
        if nr not in accounts or accounts[nr]['name'] != emri:
            print("❌ Llogaria nuk ekziston ose emri nuk përputhet.")
            return
    else:
        nr = session['account_number']

    kompani = input("🧾 Kompania për pagesë (EC, CQ, FI): ").strip().upper()
    if kompani not in ["EC", "CQ", "FI"]:
        print("❌ Kompania e pavlefshme. Lejohen vetëm EC, CQ, FI.")
        return

    shuma = input("💸 Shuma për pagesë: ").strip()
    try:
        shuma = float(shuma)
    except ValueError:
        print("❌ Shuma e pavlefshme.")
        return
    if shuma <= 0:
        print("❌ Shuma duhet të jetë më e madhe se 0.")
        return
    if not session['is_admin']:
        if paidbills_today + shuma > 2000:
            print("🚫 Kufiri maksimal ditor për pagesë faturash për përdorues standard është 2000€.")
            return
    if accounts[nr]['balance'] < shuma:
        print("🚫 Balanca e pamjaftueshme.")
        return

    accounts[nr]['balance'] -= shuma

    if not session['is_admin']:
        paidbills_today += shuma  # track daily paybill

    print(f"✅ U pagua fatura për {kompani} me {shuma:.2f}€ nga llogaria {nr}.")

    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("03", nr, shuma, kompani) + "\n")
    regjistro_csv("03", "Faturë", accounts[nr]['name'], shuma, kompani)

pending_accounts = {}

def krijo_llogari():
    if not session['is_admin']:
        print("❌ Vetëm administratori mund të krijojë llogari të reja.")
        return

    nr_input = input("🆕 Numri i llogarisë (5 shifra): ").strip()
    if not nr_input.isdigit() or len(nr_input) != 5:
        print("❌ Numri i llogarisë duhet të përmbajë saktësisht 5 shifra.")
        return
    nr = nr_input

    if nr in accounts or nr in pending_accounts:
        print("⚠️ Llogaria ekziston tashmë.")
        return

    emri = input("👤 Emri i përdoruesit (max 20 karaktere): ").strip()
    if len(emri) > 20:
        print("⚠️ Emri tejkalon kufirin maksimal prej 20 karakterësh.")
        return

    fjalekalimi = password_me_yje("🔑 Fjalëkalimi: ")

    balanca_input = input("💰 Balanca fillestare: ").strip()
    try:
        balanca = float(balanca_input)
    except ValueError:
        print("❌ Shuma e pavlefshme.")
        return
    if balanca < 0 or balanca > 99999.99:
        print("🚫 Balanca duhet të jetë midis 0 dhe 99999.99€.")
        return

    # RUHET SI PENDING – nuk shtohet në accounts derisa të bëhet logout
    pending_accounts[nr] = {
        "name": emri,
        "status": "A",
        "balance": balanca,
        "password": fjalekalimi
    }

    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("05", nr, balanca, emri) + "\n")
    regjistro_csv("05", "Krijo", emri, balanca, nr)

    print(f"✅ Llogaria {nr} për {emri} u krijua me sukses (do të aktivizohet pas logout-it).")


def fshij_llogari():
    if not session['is_admin']:
        print("❌ Vetëm administratori mund të fshijë llogari.")
        return
    nr = input("❌ Numri i llogarisë për fshirje: ").strip().zfill(5)
    if nr not in accounts:
        print("⚠️ Llogaria nuk ekziston.")
        return
    emri = input("👤 Emri i përdoruesit të llogarisë: ").strip()
    if accounts[nr]['name'] != emri:
        print("❌ Emri nuk përputhet me llogarinë.")
        return
    konfirmo = input("❗ Je i sigurt që dëshiron të fshish këtë llogari? (po/jo): ").strip().lower()
    if konfirmo != "po":
        print("❌ Veprimi u anullua.")
        return
    del accounts[nr]
    ruaj_accounts()
    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("06", nr, "00000.00", emri) + "\n")
    regjistro_csv("06", "Fshij", emri, 0, nr)
    print(f"✅ Llogaria {nr} u fshi me sukses.")

def çaktivizo_llogari():
    if not session['is_admin']:
        print("❌ Vetëm administratori mund të çaktivizojë llogari.")
        return
    nr = input("🚫 Numri i llogarisë për çaktivizim: ").strip().zfill(5)
    if nr not in accounts:
        print("⚠️ Llogaria nuk ekziston.")
        return
    emri = input("👤 Emri i mbajtësit të llogarisë: ").strip()
    if accounts[nr]['name'] != emri:
        print("❌ Emri nuk përputhet me llogarinë.")
        return
    if accounts[nr]['status'] == 'D':
        print("⚠️ Llogaria është tashmë e çaktivizuar.")
        return
    accounts[nr]['status'] = 'D'
    ruaj_accounts()
    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("07", nr, "00000.00", "00") + "\n")
    regjistro_csv("07", "Çaktivizo", emri, 0, nr)
    print(f"✅ Llogaria {nr} u çaktivizua me sukses.")


def ndrysho_plan():
    if not session['is_admin']:
        print("❌ Vetëm administratori mund të ndryshojë planin e llogarive.")
        return

    nr = input("🔁 Numri i llogarisë për ndryshim plani: ").strip().zfill(5)
    if nr not in accounts:
        print("⚠️ Llogaria nuk ekziston.")
        return

    emri = input("👤 Emri i mbajtësit të llogarisë: ").strip()
    if accounts[nr]['name'] != emri:
        print("❌ Emri nuk përputhet me llogarinë.")
        return

    plani_ri = input("📝 Vendos planin e ri (SP/NP): ").strip().upper()
    if plani_ri not in ["SP", "NP"]:
        print("❌ Plani duhet të jetë SP ose NP.")
        return
    
    if accounts[nr].get('plan', 'SP') == plani_ri:
        print(f"ℹ️ Llogaria tashmë është në planin {plani_ri}.")
        return

   
    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("08", nr, "00000.00", plani_ri) + "\n")
    regjistro_csv("08", "Ndrysho Plan", emri, 0, plani_ri)

    print(f"✅ Plani për llogarinë {nr} ({emri}) u ndryshua në {plani_ri}.")


def shfaq_historik():
    if not os.path.exists("data/session_transactions.txt"):
        print("📂 Nuk ka historik transaksioneh.")
        return
    nr = session['account_number']
    print(ngjyros(f"\n📜 Historiku për llogarinë {nr}:"))
    with open("data/session_transactions.txt", "r") as f:
        for rresht in f:
            if nr in rresht:
                print(rresht.strip())

def logout():
    if not session['logged_in']:
        print("❌ Nuk jeni të kyçur.")
        return

    # Regjistro logout në historik
    with open("data/session_transactions.txt", "a") as f:
        f.write(formo_transaksion("00", "00000", "00000.00", "00") + "\n")

    # Aktivizo llogaritë e reja të krijuara gjatë këtij sesioni
    if pending_accounts:
        for nr, info in pending_accounts.items():
            accounts[nr] = info
        pending_accounts.clear()
        print("✅ Llogaritë e reja u aktivizuan pas logout-it.")

    # Apliko depozitat në pritje
    if pending_deposits:
        for nr, shuma in pending_deposits.items():
            if nr in accounts:
                accounts[nr]['balance'] += shuma
        pending_deposits.clear()
        print("✅ Depozitat në pritje u aplikuan pas logout-it.")

    # Ruaj gjendjen e fundit
    ruaj_accounts()

    # Reset sesionin
    session.update({
        "logged_in": False,
        "account_number": None,
        "user_name": None,
        "is_admin": False
    })
    session['withdrawn_this_session'] = 0.0  # reset on logout
    session['transferred_this_session'] = 0.0  # reset on logout
    session['deposited_this_session'] = 0.0  # reset on logout
    session['paidbills_this_session'] = 0.0  # reset on logout

    print("👋 U çkyçët me sukses.")


def shfaq_komandat():
    print(ngjyros("\n📘 Komandat në dispozicion:"))
    print("🔹 çkyçu – Çkyçu nga llogaria")  # changed from 'logout'
    print("🔹 dalje – Dil nga aplikacioni")
    print("🔹 bilanci – Shfaq balancën tënde aktuale")
    print("🔹 depozitë – Shto para në llogarinë tënde")
    print("🔹 tërheqje – Tërhiq para nga llogaria")
    print("🔹 transfero – Transfero para në një llogari tjetër")
    print("🔹 faturë – Paguaj një faturë (EC, CQ, FI)")
    print("🔹 ndryshofjalekalim – Ndrysho fjalëkalimin")
    print("🔹 historik – Shfaq historikun e transaksioneve")
    if session['is_admin']:
        print("🔸 krijo – Krijo llogari të re")
        print("🔸 fshijllogari – Fshij një llogari ekzistuese")
        print("🔸 çaktivizo – Çaktivizo një llogari")
        print("🔸 ndryshoplan – Ndrysho planin e një llogarie")
        print("🔸 bilancet – Shfaq balancat e të gjithë përdoruesve")

def kryesore():
    global withdrawn_today, deposited_today, transferred_today, paidbills_today
    if not lexo_accounts():
        return
    while True:
        if not session['logged_in']:
            login()
            continue
        komanda = input(ngjyros("\n💬 Komanda > ")).strip().lower()
        if komanda == "çkyçu":
            logout()
        elif komanda == "dalje":
            print("👋 Faleminderit që përdorët sistemin bankar.")
            withdrawn_today = 0.0
            deposited_today = 0.0
            transferred_today = 0.0
            paidbills_today = 0.0
            break
        elif komanda == "depozitë":
            depozite()
        elif komanda == "tërheqje":
            terheqje()
        elif komanda == "transfero":
            transfero()
        elif komanda == "faturë":
            paguaj_fature()
        elif komanda == "krijo":
            krijo_llogari()
        elif komanda == "fshijllogari":
            fshij_llogari()
        elif komanda == "çaktivizo":
            çaktivizo_llogari()
        elif komanda == "ndryshoplan":
            ndrysho_plan()
        elif komanda == "ndryshofjalekalim":
            ndrysho_fjalekalim()
        elif komanda == "historik":
            shfaq_historik()
        elif komanda == "bilancet":
            shfaq_te_gjithe_balancat()
        elif komanda == "bilanci":
            shfaq_balancen_time()
        else:
            print("⚠️ Komandë e panjohur. Përdorni 'dalje' për të dalë ose 'çkyçu' për t'u çkyçur.")

if __name__ == "__main__":
    inicializo_csv_nqs_sduhet()
    kryesore()
