import sys
import yaml
import argparse
import subprocess


USR="dtu"
URL="http://127.0.0.1:8200"


class Vault:
    def __init__(self, url: str, user: str) :
        self.url = url
        self.user = user



    def list(self, path:str = "") -> list[str] :
        cmd = [
            "docker", "exec",
            "-e", f"VAULT_ADDR={self.url}",
            "-e", f"VAULT_TOKEN={self.user}",
            "vault",
            "vault", "kv", "list", "-format=yaml", "dtu" + path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return([])

        try:
            data = yaml.safe_load(result.stdout)

            if isinstance(data, dict) : keys = data.get("data", {}).get("keys", [])
            elif isinstance(data, list) : keys = data
            else : keys = []
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            return([])

        paths = []
        for key in keys:
            next = f"{path}{key}"
            if key.endswith('/') : paths.extend(self.list(next))
            else : paths.append(next)

        return(paths)



    def get(self, path:str) -> any :
        cmd = [
            "docker", "exec",
            "-e", f"VAULT_ADDR={self.url}",
            "-e", f"VAULT_TOKEN={self.user}",
            "vault",
            "vault", "kv", "get", "-format=yaml", f"dtu{path}"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return({})

        try:
            data = yaml.safe_load(result.stdout)
            return(data.get("data", {}).get("data", {}))
        except Exception as e:
            print(f"❌ Error reading secret at {path}: {e}")
            return({})


    def load(self,node, path:str = "") :
        secrets:dict = {}

        for key, value in node.items() :
            if isinstance(value, dict) :
                parts = filter(None, [path, key])
                next = "/".join(parts)
                self.load(value,next)
            else :
                 secrets[key] = value

        if (secrets) :
            self.save(path,secrets)



    def save(self,path:str, data:any) :
        cmd = [
            "docker", "exec",
            "-e", f"VAULT_ADDR={self.url}",
            "-e", f"VAULT_TOKEN={self.user}",
            "vault",
            "vault", "kv", "put", "dtu/"+path
        ]

        for k, v in data.items():
            cmd.append(f"{k}={v}")

        subprocess.run(cmd, shell=False)




class CustomParser(argparse.ArgumentParser):
    def error(self, message):
            print(f"\n❌ Error: {message}")
            print("Tip: Use 'vault --help' to see the full list of available commands.\n")
            self.exit(2)



if __name__ == "__main__" :
    parser = CustomParser(description="Vault Service Tool")

    parser.add_argument("-a", "--addr", default=URL, help="Vault server address")
    parser.add_argument("-u", "--user", default=USR, help="Vault username/token")

    subparsers = parser.add_subparsers(dest="command", required=True,metavar="[options] command ...")

    ls_parser = subparsers.add_parser("ls", help="List secrets [path]")
    ls_parser.add_argument("path", nargs="?", default="/", help="Vault path to list (e.g. databases/)")

    load_parser = subparsers.add_parser("load", help="Load secrets from <file>")
    load_parser.add_argument("file", help="Path to the source file (yaml)")

    if (len(sys.argv) < 2) :
        print()
        parser.print_help()
        print()
        sys.exit(0)

    args = parser.parse_args()

    addr = args.addr
    user = args.user
    #file = args.file

    vault:Vault = Vault(addr,user)

    if (args.command == "ls") :
        path = args.path

        if (not path.endswith("/")) :
            path = path + "/"

        if (not path.startswith("/")) :
            path = "/" + path

        secrets = vault.list(path)

        print()
        print("--- Secrets ---")
        for s in secrets:
            secret = str(vault.get(s))
            print(s+" -> "+secret)
        print()


    if (args.command == "load") :
        try:
            print()
            with open(args.file,"r") as f :
                config = yaml.safe_load(f)

                for key, value in config.items() :
                     vault.load(value)
            print()

        except FileNotFoundError:
                print(f"❌ {args.file} not found.")
        except Exception as e:
                print(f"❌ An error occurred: {e}")

