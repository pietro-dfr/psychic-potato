from typing import Optional, List

def is_valid_cpf(cpf: str) -> bool:
    if len(cpf) != 11:
        return False
    for c in cpf:
        if c < "0" or c > "9":
            return False
    all_equal = True
    for i in range(1, 11):
        if cpf[i] != cpf[0]:
            all_equal = False
            break
    if all_equal:
        return False
    total = 0
    weight = 10
    for i in range(9):
        total += int(cpf[i]) * weight
        weight -= 1
    digit1 = (total * 10) % 11
    if digit1 == 10:
        digit1 = 0
    total = 0
    weight = 11
    for i in range(10):
        total += int(cpf[i]) * weight
        weight -= 1
    digit2 = (total * 10) % 11
    if digit2 == 10:
        digit2 = 0
    return digit1 == int(cpf[9]) and digit2 == int(cpf[10])

def is_valid_phone(phone: str) -> bool:
    if len(phone) != 11:
        return False
    for c in phone:
        if c < "0" or c > "9":
            return False
    valid_ddds = [
        "11","12","13","14","15","16","17","18","19",
        "21","22","24","27","28","31","32","33","34","35","37","38",
        "41","42","43","44","45","46","47","48","49",
        "51","53","54","55","61","62","64","63","65","66","67","68","69",
        "71","73","74","75","77","79","81","82","83","84","85","86","87","88","89",
        "91","92","93","94","95","96","97","98","99"
    ]
    ddd = phone[:2]
    return ddd in valid_ddds

class User:
    def __init__(self, name: str, cpf: str, address: str, phone: str, password: str) -> None:
        self.name = name
        self.cpf = cpf
        self.address = address
        self.phone = phone
        self.password = password

class BankAccount(User):
    def __init__(self, name: str, cpf: str, address: str, phone: str, password: str, account_number: int) -> None:
        super().__init__(name, cpf, address, phone, password)
        self.account_number = account_number
        self.balance = 0.0
        self.pix_keys = [cpf]  # chave PIX principal é o CPF

    def deposit(self, amount: float) -> bool:
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw(self, amount: float) -> bool:
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

class Bank:
    def __init__(self) -> None:
        self.users: List[BankAccount] = []
        self.next_account_number: int = 1000

    def register_user(self, name: str, cpf: str, address: str, phone: str, password: str) -> bool:
        if not is_valid_cpf(cpf):
            print("CPF inválido")
            return False
        if not is_valid_phone(phone):
            print("Telefone inválido")
            return False
        if self.find_user(cpf) is not None:
            print("CPF já cadastrado")
            return False
        account = BankAccount(name, cpf, address, phone, password, self.next_account_number)
        self.next_account_number += 1
        self.users.append(account)
        print(f"Usuário {name} registrado com conta {account.account_number}")
        return True

    def find_user(self, cpf: str) -> Optional[BankAccount]:
        for user in self.users:
            if user.cpf == cpf:
                return user
        return None

    def find_user_by_pix(self, pix_key: str) -> Optional[BankAccount]:
        for user in self.users:
            if pix_key in user.pix_keys:
                return user
        return None

    def authenticate(self, cpf: str, password: str) -> Optional[BankAccount]:
        user = self.find_user(cpf)
        if user and user.password == password:
            return user
        return None

    def list_users(self) -> None:
        if len(self.users) == 0:
            print("Não há usuários cadastrados!")
            return
        print("=== Usuários ===")
        for u in self.users:
            print(f"Nome: {u.name}, CPF: {u.cpf}, Conta: {u.account_number}, Saldo: R$ {u.balance:.2f}")

    def transfer_by_pix(self, from_user: BankAccount, pix_key: str, amount: float) -> bool:
        to_user = self.find_user_by_pix(pix_key)
        if to_user is None:
            print("Chave PIX não encontrada.")
            return False
        if amount <= 0:
            print("Valor inválido.")
            return False
        if from_user.withdraw(amount):
            to_user.deposit(amount)
            print(f"Transferência de R$ {amount:.2f} para PIX {pix_key} realizada.")
            return True
        else:
            print("Saldo insuficiente.")
            return False

    def transfer_by_account(self, from_user: BankAccount, to_account_number: int, amount: float) -> bool:
        to_user = None
        for u in self.users:
            if u.account_number == to_account_number:
                to_user = u
                break
        if to_user is None:
            print("Conta destino não encontrada.")
            return False
        if amount <= 0:
            print("Valor inválido.")
            return False
        if from_user.withdraw(amount):
            to_user.deposit(amount)
            print(f"Transferência de R$ {amount:.2f} para conta {to_account_number} realizada.")
            return True
        else:
            print("Saldo insuficiente.")
            return False

bank = Bank()

def register() -> None:
    name = input("Nome: ").strip()
    cpf = input("CPF (11 dígitos): ").strip()
    address = input("Endereço: ").strip()
    phone = input("Telefone (11 dígitos): ").strip()
    password = input("Senha: ").strip()
    bank.register_user(name, cpf, address, phone, password)

def login() -> None:
    cpf = input("CPF: ").strip()
    password = input("Senha: ").strip()
    user = bank.authenticate(cpf, password)
    if user:
        print(f"Bem-vindo {user.name}!")
        user_menu(user)
    else:
        print("Login falhou")

def user_menu(user: BankAccount) -> None:
    while True:
        print("\n1 - Ver saldo\n2 - Depositar\n3 - Sacar\n4 - Transferir\n5 - Logout")
        option = input("Opção: ").strip()
        if option == '1':
            print(f"Saldo: R$ {user.balance:.2f}")
        elif option == '2':
            val = input("Valor para depósito: ").strip()
            try:
                amount = float(val)
                if user.deposit(amount):
                    print("Depósito realizado")
                else:
                    print("Valor inválido")
            except:
                print("Entrada inválida")
        elif option == '3':
            val = input("Valor para saque: ").strip()
            try:
                amount = float(val)
                if user.withdraw(amount):
                    print("Saque realizado")
                else:
                    print("Saldo insuficiente ou valor inválido")
            except:
                print("Entrada inválida")
        elif option == '4':
            print("\n1 - Transferir por PIX\n2 - Transferir por número da conta")
            transfer_option = input("Escolha a forma de transferência: ").strip()
            if transfer_option == '1':
                pix_key = input("Digite a chave PIX do destinatário (CPF): ").strip()
                try:
                    amount = float(input("Valor: ").strip())
                    bank.transfer_by_pix(user, pix_key, amount)
                except:
                    print("Entrada inválida")
            elif transfer_option == '2':
                val = input("Conta destino: ").strip()
                try:
                    destination_account = int(val)
                    amount = float(input("Valor: ").strip())
                    bank.transfer_by_account(user, destination_account, amount)
                except:
                    print("Entrada inválida")
            else:
                print("Opção inválida")
        elif option == '5':
            print("Logout")
            break
        else:
            print("Opção inválida")

def list_users() -> None:
    bank.list_users()

def main() -> None:
    while True:
        print("\n1 - Registrar\n2 - Login\n3 - Listar Usuários\n4 - Sair")
        option = input("Opção: ").strip()
        if option == '1':
            register()
        elif option == '2':
            login()
        elif option == '3':
            list_users()
        elif option == '4':
            print("Tchau")
            break
        else:
            print("Inválido")

if __name__ == "__main__":
    main()
