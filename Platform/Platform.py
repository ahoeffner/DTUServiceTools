import os
import sys
import argparse
from enum import Enum
from pathlib import Path

from Git import Git
from Docker import Docker
from DockerVolume import DockerVolume



HOME = None

FORCE = False
VERBOSE = False

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
    def install(self):
        print("📦 Installing platform:\n")
        self.git()

        print()
        self.volumes()

        print()
        self.docker()


    def update(self):
        print("🔄 Updating platform:\n")


    def start(self, services: list[str]):
        print("📈 Starting services:\n")


    def stop(self, services: list[str]):
        print("📉 Stopping services:\n")


    def git(self):
        git = Git(FORCE,VERBOSE)
        git.update()


    def docker(self):
        docker = Docker(FORCE,VERBOSE)
        docker.createNetwork(DOCKER.network)

        for srv in DOCKER.containers:
            docker.startContainer(Path(DOCKERPATH)/srv)


    def volumes(self):
        volume = DockerVolume(FORCE,VERBOSE)

        for vol in VOLUMES.volumes:
            volume.create(vol[0], chown=vol[1])


    def setup(self,path:str = None, secrets:str = None):
        global HOME
        global SECRETS

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

    if (args.command == None) :
        print()
        parser.print_help()
        print()
        sys.exit(0)

    FORCE = args.force
    VERBOSE = args.verbose

    platform:Platform = Platform()
    platform.setup(args.path, args.secrets)

    print(f"\n🏠 : {HOME}\n")

    match args.command:
        case "start":
            if (args.service == None): platform.start(CONTAINERS)
            else: platform.start([args.service])

        case "stop":
            if (args.service == None): platform.stop(CONTAINERS)
            else: platform.stop([args.service])

        case "update":
            platform.update()

        case "install":
            platform.install()