from test_add_metadata import run as test_add_metadata
from test_local_service import run as test_local_service


def main():
    print()
    print("#### LET'S START FUNCTIONAL TESTS ####")

    test_local_service()

    test_add_metadata()

    print("#### FUNCTIONAL TESTS ALL PASSED ####")
    print("#### BRAVOOO ####")
    print()


if __name__ == "__main__":
    main()
