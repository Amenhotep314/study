heroku pg:backups:capture --app fluxstudy
heroku pg:backups:download --app fluxstudy
pg_restore --verbose --clean --no-acl --no-owner -h localhost -U nathanlenzini -d study latest.dump
rm -f latest.dump
