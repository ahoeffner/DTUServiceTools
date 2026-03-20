import sys
import argparse

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="Service Platform Tool")

    parser.add_argument("-s", "--start", action="store_true", help="Start Development Environment")
    parser.add_argument("-u", "--update", action="store_true", help="Update Development Environment")
    parser.add_argument("-i", "--install", action="store_true", help="Install Development Environment")

    if (len(sys.argv) < 2) :
        print()
        parser.print_help()
        print()
        sys.exit(0)

    args = parser.parse_args()
