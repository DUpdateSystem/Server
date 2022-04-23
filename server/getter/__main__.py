import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r',
                        '--register',
                        dest='register_discovery_url',
                        help='register discovery server address',
                        type=str,
                        required=True)
    parser.add_argument('-b',
                        '--bind_template',
                        dest='url_template',
                        help='getter wocker bind address template',
                        type=str,
                        required=True)
    parser.add_argument('-db',
                        '--database_url',
                        dest='database_url',
                        help='database server url',
                        type=str,
                        required=False)
    args = parser.parse_args()

    if args.database_url:
        import database.config as db_config
        db_config.db_url = args.database_url

    from getter.service.main import main
    main(args.register_discovery_url, args.url_template)
