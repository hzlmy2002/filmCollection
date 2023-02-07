# API 

## Endpoint

```
https://film.thinktank007.com/api/v1/
```

## Structure
```
|--- endpoint(/api/v1/)
         |--- /view (return an dict of film {film_name:id})
         |       |--- /title
         |       |      |--- /<str:title keyword>
         |       |
         |       |--- /date
         |       |      |--- /<int:year>
         |       |      
         |       |--- /genres
         |       |      |--- /<str:genres keyword>
         |       |
         |       |--- /popular 
         |       |      |--- /<int:since year>
         |       |
         |       |--- /content
         |       |      |--- /<str:content keyword>
         |       |
         |       |--- /rating
         |
         |--- /detail (return an dict of film detail) 
                    |--- /id
                           |--- /<int:id>
         
```



