import autoIserv
import getpass
import time

def main():
    COLOR_CYAN = str(b'\x1b[36m', encoding="utf-8")
    COLOR_GREEN = str(b'\x1b[32m', encoding="utf-8")
    COLOR_YELLOW = str(b'\x1b[33m', encoding="utf-8")
    COLOR_RED = str(b'\x1b[31m', encoding="utf-8")
    COLOR_RESET = str(b'\x1b[0m', encoding="utf-8")

    print(f"{COLOR_CYAN}---------Credential creation---------{COLOR_RESET}")
    username = input(f"{COLOR_GREEN}Enter Iserv username : {COLOR_RESET}")
    while True:
        password = getpass.getpass(f"{COLOR_YELLOW}Enter Iserv password : {COLOR_RESET}")
        password_again = getpass.getpass(f"{COLOR_YELLOW}Enter Iserv password again: {COLOR_RESET}")
        if password != password_again:
            print(f"{COLOR_RED}[*] Passwords are not equal{COLOR_RESET}")
        else:
            break

    while True:
        key = getpass.getpass(f"{COLOR_RED}Enter secret credential encryption key : {COLOR_RESET}")
        key_again = getpass.getpass(f"{COLOR_RED}Enter secret credential encryption key : {COLOR_RESET}")
        if key != key_again:
            print(f"{COLOR_RED}[*] Keys are not equal{COLOR_RESET}")
        else:
            break
    print(f"{COLOR_CYAN}-------------------------------------{COLOR_RESET}")

    print(f"{COLOR_CYAN}[*] Creating Credentials{COLOR_RESET}")
    autoIserv.create_credential_file(username, password, key, "credential")
    time.sleep(0.3)
    print(f"{COLOR_CYAN}[*] Done{COLOR_RESET}")
    input(f"{COLOR_CYAN}Press Enter to exit{COLOR_RESET}")


if __name__ == "__main__":
    main()