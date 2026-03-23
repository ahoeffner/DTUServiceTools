import subprocess


class Git:
    def __init__(self,force:bool = False, verbose:bool = False):
        self.force = force
        self.verbose = verbose

    def update(self) -> bool:
        try :
            if (self.verbose) : print("\ngit pull")
            subprocess.run(["git", "pull"], check=True, capture_output=True)

        except Exception as e :
            print(f"❌ Failed to update Git: {e}\n")
            return(False)

        try :
            if (self.verbose) : print("\ngit submodule update --init --recursive")
            subprocess.run(["git", "submodule", "update", "--init", "--recursive"], check=True, capture_output=True)

        except Exception as e :
            print(f"❌ Failed to update submodules: {e}\n")
            return(False)

        return(True)