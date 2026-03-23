import subprocess


class Docker :
    def __init__(self,force:bool = False, verbose:bool = False):
        self.force = force
        self.verbose = verbose


    def createNetwork(self,name:str) -> bool :
        try :
            networks = subprocess.run(
                ["docker", "network", "ls", "--format", "{{.Name}}"],
                capture_output=True, text=True, check=True).stdout.splitlines()

            if name in networks:
                print(f"✅ Docker network {name} already exists.\n")
                return(True)

            if (self.verbose) : print("\ndocker network create "+name)
            subprocess.run(["docker", "network", "create", name], check=True)
            print(f"✅ Docker network {name} was installed.\n")

            return(True)

        except Exception as e :
            print(f"❌ Failed to manage Docker networks: {e}\n")
            return(False)


    def startContainer(self,path:str) -> bool :
        try :
            if (self.verbose) : print(f"\ndocker compose -f {path} up -d")
            subprocess.run(
                ["docker", "compose", "up", "-d"],
                cwd=path,             # Runs the command in the right folder
                check=True,           # Raises CalledProcessError if the command fails
                capture_output=True,  # Captures stdout and stderr
                text=True             # Returns output as strings instead of bytes
            )

            print(f"✅ Docker container @{path} started successfully")
            return(True)

        except subprocess.CalledProcessError as e:
            print(f"❌ Docker Compose failed with error: {e.stderr}")
        except Exception as e :
            print(f"❌ Failed to start container {path}: {e}\n")
            return(False)


