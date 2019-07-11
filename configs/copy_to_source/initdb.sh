echo "
	SELECT 'CREATE DATABASE iam'
	WHERE NOT EXISTS (SELECT FROM pg_database where datname = 'iam')\gexec
" | psql -Uwagglenet

echo "
	SELECT 'CREATE DATABASE backplane'
	WHERE NOT EXISTS (SELECT FROM pg_database where datname = 'backplane')\gexec
" | psql -Uwagglenet
