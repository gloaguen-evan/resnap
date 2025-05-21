import argparse


def main(run_local: bool = True, run_metadata: bool = True, run_boto: bool = True) -> None:
    """
    Main function to run functional tests.
    Args:
        run_local (bool): Flag to run local tests.
        run_metadata (bool): Flag to run add_metadata tests.
        run_boto (bool): Flag to run boto tests.
    """
    print()
    print("#### LET'S START FUNCTIONAL TESTS ####")

    if run_local:
        from test_local_service import run as test_local_service
        test_local_service()

    if run_metadata:
        from test_add_metadata import run as test_add_metadata
        test_add_metadata()

    if run_boto:
        from test_boto_service import run as test_boto_service
        test_boto_service()

    print("#### FUNCTIONAL TESTS ALL PASSED ####")
    print("#### BRAVOOO ####")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run functional tests.")

    parser.add_argument("--local", action="store_true", help="Run local tests")
    parser.add_argument("--no-local", dest="local", action="store_false", help="Do not run local tests")
    parser.set_defaults(local=True)

    parser.add_argument("--metadata", action="store_true", help="Run add_metadata tests")
    parser.add_argument("--no-metadata", dest="metadata", action="store_false", help="Do not run add_metadata tests")
    parser.set_defaults(metadata=True)

    parser.add_argument("--boto", action="store_true", help="Run boto tests")
    parser.add_argument("--no-boto", dest="boto", action="store_false", help="Do not run boto tests")
    parser.set_defaults(boto=True)

    args = parser.parse_args()
    main(args.local, args.metadata, args.boto)
