# Deploy on heroku


## Initial
* Have the heroku cli

Once: 
```
heroku login 
```

Set secrets 
```
heroku config:set INFLUX_TOKEN=TaFEe3NXSIEKqJ...
heroku config:set MAPBOX_TOKEN=bla
```

Create git remote for heroku
```
heroku create my-dash-app 
```

## Deploy
```
git push heroku main
```
