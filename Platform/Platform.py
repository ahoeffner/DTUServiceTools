import os
import sys
import argparse
import subprocess
import platform as osp

from enum import Enum
from pathlib import Path

from Git import Git
from Maven import Maven
from Docker import Docker



HOME = None

FORCE = False
VERBOSE = False
PLATFORM = None

SECRETS = None

LIBPATH = "libraries"
DOCKERPATH = "docker"

JAVALIBS = ["spring","fusion"]
CONTAINERS = ["kafka", "vault", "keycloak", "registry", "postgres"]

class TOOLS(Enum) :
    Git    = ["git"    , "--version"]
    Java   = ["java"   , "-version"]
    Maven  = ["mvn"    , "-version"]
    Docker = ["docker" , "--version"]

class VOLUMES :
    volumes = [
        ["kafka-data",True],
        ["kafka-logs",True],
        ["vault-data",True],
        ["vault-logs",True],
        ["kafka-config",True],
        ["kafka-secrets",True]]

class DOCKER :
    network = "dtu-services"
    containers = CONTAINERS



class Platform:
    def check(self) -> bool:
        check:bool = True

        print("Checking system dependencies...\n" + "-"*32)

        for tool in TOOLS :
            if (not self.checkTool(tool.name,tool.value)) :
                check = False

        if (check): print(f"   ✅ system dependencies are satisfied.")
        else: print(f"   ❌ system dependencies are NOT satisfied.")

        return(check)



    def checkTool(self,name:str,command:str) -> bool:
        try:
            if (VERBOSE) : print("\n.  "+" ".join(command))
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"   ✅ {name} is installed.")
            return(True)
        except :
            print(f"   ❌ {name} is NOT installed or not in PATH.")
            return(False)



    def install(self) -> bool:
        print("📦 Installing platform:\n")

        docker:Docker = Docker(FORCE,VERBOSE)

        if (not self.git() and not FORCE) :
            return(False)

        print()

        if (not self.maven() and not FORCE) :
            return(False)

        print()

        if (not self.volumes(docker) and not FORCE) :
            return(False)

        print()

        if (not self.containers(docker) and not FORCE) :
            return(False)

        print()
        return(True)



    def update(self) -> bool:
        print("🔄 Updating platform:\n")

        if (not self.git() and not FORCE) :
            return(False)

        print()

        if (not self.maven() and not FORCE) :
            return(False)

        return(True)




    def start(self, services:list[str] = None) -> bool:
        docker:Docker = Docker(FORCE,VERBOSE)

        if (services != None) :
            for srv in services:
                if (not self.container(docker,srv)):
                    return(False)
            return(True)


        if (not self.containers(docker) and not FORCE) :
            return(False)



    def stop(self, services: list[str] = None) -> bool:
        docker:Docker = Docker(FORCE,VERBOSE)

        if (not services == None):
            for srv in services:
                if (not self.container(docker,srv,False)):
                    return(False)
            return(True)


        if (not self.containers(docker,False) and not FORCE) :
            return(False)

        return(True)



    def git(self) -> bool:
        print("🔄 Updating sources:")

        git = Git(FORCE,VERBOSE)
        return(git.update())



    def maven(self) -> bool:
        print("🔄 Installing libraries:")

        mvn = Maven(FORCE,VERBOSE)

        for lib in JAVALIBS:
            if (not mvn.install(Path(LIBPATH)/lib) and not FORCE):
                return(False)

        return(True)



    def containers(self, docker:Docker, start:bool = True) -> bool:

        if (start) :
            print("🔄 Checking docker networks:")
            if (not docker.network(DOCKER.network)):
                return(False)

        if (start) : print("🔄 Starting services:")
        else : print("🔄 Stopping services:")

        for srv in CONTAINERS:
            if (not self.container(docker,srv,start)):
                return(False)

        return(True)


    def container(self, docker:Docker, name:str, start:bool = True) -> bool:
        if (start) :
            if (not docker.start(Path(DOCKERPATH)/name)):
                return(False)

        else :
            if (not docker.stop(Path(DOCKERPATH)/name)):
                return(False)

        return(True)



    def volumes(self, docker:Docker):
        print("🔄 Checking docker volumes:")

        for vol in VOLUMES.volumes:
            if (not docker.volume(vol[0], chown=vol[1])):
                return(False)

        return(True)



    def setup(self,path:str = None, secrets:str = None):
        global HOME
        global SECRETS
        global PLATFORM

        PLATFORM = osp.system().lower()
        if (PLATFORM == "darwin") : PLATFORM = "mac"

        if (path != None):
            HOME = os.path.abspath(path)

            if (not os.path.isdir(HOME)):
                print(f"❌ Error: Path '{HOME}' does not exist.")
                sys.exit(1)

            os.chdir(HOME)

            if (secrets != None):
                SECRETS = os.path.abspath(secrets)
            return

        if (HOME == None):
            HOME = os.path.dirname(os.path.abspath(__file__))

            if getattr(sys, 'frozen', False):
                cwd = os.getcwd()
                rel = sys.argv[0]
                HOME = os.path.normpath(os.path.join(cwd,rel))

        if (not os.path.isdir(HOME)):
            print(f"❌ Error: Path '{HOME}' does not exist.")
            sys.exit(1)


        dir = Path(HOME).parent

        if (dir.name.lower() in ["mac", "linux", "install", "bin"]):
            dir = dir.parent

        os.chdir(dir)

        HOME = str(dir)

        if (secrets != None):
            SECRETS = os.path.abspath(secrets)



    def path(self):
        return(HOME)

    def libpath(self):
        return(LIBPATH)

    def dockerpath(self):
        return(DOCKERPATH)


class CustomParser(argparse.ArgumentParser):
    def error(self, message):
            print(f"\n❌ Error: {message}")
            print("Tip: Use 'platform --help' to see the full list of available commands.\n")
            self.exit(2)



if __name__ == "__main__" :
    helptext = f"services:\n  " + "\n  ".join(CONTAINERS)

    parser = CustomParser(
            description="🚀 Service Platform Development Tool",
            formatter_class=argparse.RawTextHelpFormatter,
            usage="platform COMMAND [options]"
        )

    parser.add_argument("-f", "--force",action="store_true",help="Force commands")
    parser.add_argument("-v", "--verbose",action="store_true",help="Print commands")
    parser.add_argument("-c", "--check",action="store_true",help="Check prerequisites")
    parser.add_argument("-p", "--path", type=str, metavar="PATH", help="Set installation path")
    parser.add_argument("-s", "--secrets", type=str, metavar="PATH", help="Set path to vault secrets")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    start_parser = subparsers.add_parser(
        "start",
        help="start "+helptext,
        formatter_class=argparse.RawTextHelpFormatter
    )

    start_parser.add_argument(
        "service",
        nargs="?",
        choices=CONTAINERS,
    )

    stop_parser = subparsers.add_parser(
        "stop",
        help="stop "+helptext,
        formatter_class=argparse.RawTextHelpFormatter
    )

    stop_parser.add_argument(
        "service",
        nargs="?",
        choices=CONTAINERS,
    )

    subparsers.add_parser("update", help="Refresh all dependencies")
    subparsers.add_parser("install", help="Install the full development environment")

    if (len(sys.argv) < 2) :
        print()
        parser.print_help()
        print()
        sys.exit(0)

    args = parser.parse_args()

    if (args.command == None and not args.check) :
        print()
        parser.print_help()
        print()
        sys.exit(0)

    FORCE = args.force
    VERBOSE = args.verbose

    platform:Platform = Platform()
    platform.setup(args.path, args.secrets)

    print("\n\n"+"-"*64)
    print(f"  🏠 home: {HOME}  os: {PLATFORM}")
    print("-"*64)
    print("\n")

    if (args.check):
        if (not platform.check() and not FORCE) :
            sys.exit(1)
        print()

    match args.command:
        case "start":
            if (args.service == None):
                print("🔄 Starting all services:\n")
                platform.start()
            else:
                print("🔄 Starting services:")
                platform.start([args.service])

        case "stop":
            if (args.service == None):
                print("🔄 Stopping all services:\n")
                platform.stop()
            else:
                print("🔄 Stopping services:")
                platform.stop([args.service])

        case "update":
            platform.update()

        case "install":
            platform.install()

    print()