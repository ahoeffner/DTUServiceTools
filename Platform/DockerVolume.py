import subprocess


class DockerVolume:
    verbose:bool = False

    def __init__(self,force:bool = False, verbose:bool = False):
        self.force = force
        self.verbose = verbose

        result = subprocess.run(
            ["docker", "volume", "ls", "-q"],
            capture_output=True, text=True, check=True
        )

        self.volumes = result.stdout.splitlines()


    def create(self,name:str, chown:bool = False) -> bool:
        try :
            if (not self.force and name in self.volumes) :
                print(f"✅ Docker volume {name} already exists.")
                return(True)

            if (self.verbose) : print("\ndocker volume create "+name)
            subprocess.run(["docker", "volume", "create", name], check=True, capture_output=True)

            if (chown) :
                if (self.verbose) : print("docker run --rm -v "+name+":/mnt busybox chown -R 1000:1000 /mnt")
                subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", f"{name}:/mnt",
                    "busybox", "chown", "-R", "1000:1000", "/mnt"
                ],
                check=True, capture_output=True)

            print(f"✅ Docker volume {name} was installed.")

            return(True)

        except Exception as e :
            print(f"❌ Failed to manage Docker volumes: {e}\n")
            return(False)