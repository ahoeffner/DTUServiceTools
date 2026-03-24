import subprocess


class Maven :
    def __init__(self,force:bool = False, verbose:bool = False):
        self.force = force
        self.verbose = verbose


    def install(self,path:str) -> bool :
        try :
            if (self.verbose) : print(f"   mvn clean install -f {path}")

            subprocess.run(
                ["mvn", "clean", "install"],
                cwd=path,             # Runs the command in the right folder
                check=True,           # Raises CalledProcessError if the command fails
                capture_output=True,  # Captures stdout and stderr
                text=True             # Returns output as strings instead of bytes
            )

            print(f"   ✅ Maven library '{path}' installed successfully")
            return(True)

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Maven library '{path}' installation failed")
            if (self.verbose) : print(e.stderr)
        except Exception as e :
            print(f"   ❌ Maven library '{path}' installation failed: {e}\n")
            return(False)
