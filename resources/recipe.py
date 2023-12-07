from flask import request
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

# resources 폴더 안에 만드는 파일에는,
# API 를 만들기 위한 클래스를 작성한다.

# API 를 만들기 위해서는 flask_restful 라이브러리의
# Resource 클래스를 상속해서 만들어야 한다.

class RecipeListResource(Resource):

    # http Method 와 동일한 함수명으로 오버라이딩!

    def post(self):
        
        # 1. 클라이언트가 보내준 데이터가 있으면,
        #    그 데이터를 먼저 받아준다.

        data = request.get_json()

        print(data)

        # 2. 받아온 레시피데이터를
        #    DB에 저장해야 한다.

        try :
            # 2-1. db에 연결하는 코드(틀)
            connection = get_connection()

            # 2-2. 쿼리문 만들기 - insert 쿼리만들기.
            query = '''insert into recipe
                        (name, description, num_of_servings,
                            cook_time, directions)
                        values
                        (%s,%s,%s,%s,%s);'''
            # 2-3. 위의 쿼리에 매칭되는 변수를 처리해 준다.
            #       단, 라이브러리 특성상, 튜플로 만들어야 한다.
            record = ( data['name'] , data['description'] , 
                      data['num_of_servings'], data['cook_time'],
                         data['directions'])

            # 2-4. 커서를 가져온다.
            cursor = connection.cursor()

            # 2-5. 위의 쿼리문을, 커서로 실행한다.
            cursor.execute(query, record)

            # 2-6. 커밋해줘야, DB에 완전히 반영된다.
            connection.commit()

            # 2-7 자원해제
            cursor.close()
            connection.close() 

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            # 유저한테 알려줘야 한다. => response 해준다.
            return{"result":"fail", "error": str(e)},500

        # 3. DB에 잘 저장되었으면,
        #    클라이언트에게 응답해준다.
        #    보내줄 정보(json)과 http 상태코드를
        #    리턴한다.


        return {"result":"success"} , 200
   
    def get(self) :
        
        # 1. 클라이언트로부터 데이터를 받아온다.
        # 없다. 할 필요 없음.

        # 2. DB에 저장된 데이터를 가져온다.
        try:
            connection = get_connection()

            query = '''select *
                        from recipe;'''
            
            # 중요!!!!!!
            # Select 문에서!!! 커서를 만들 때에는 
            # dictionary = True로 해준다.
            # 왜? 리스트와 딕셔너리 형태로 가져오기 때문에
            # 클라이언트에게 json 형식으로 보내줄 수 있다.
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query)

            result_list = cursor.fetchall() #모든 데이터 다 꺼내오는 함수

            print(result_list)

            # datetime 은 파이썬에서 사용하는 데이터타입으므로
            # json 형식이 아니다. 따라서
            # json은 문자열이나 숫자만 가능하므로
            # datetime을 문자열로 바꿔줘야 한다.★★★★★★

            i = 0
            for row in result_list :
                result_list[i]['created_at']= row['created_at'].isoformat()
                result_list[i]['updated_at']= row['updated_at'].isoformat()
                i = i + 1

            print()
            print(result_list)
            print()


            cursor.close()
            connection.close()
            

        except Error as e : 
            print(e)
            cursor.close()
            connection.close()
            #클라이언트에게 에러라고 보내줘야 한다.
            return {"result":"fail","error":str(e)}, 500

        return {"result": "success","items":result_list,"count": len(result_list)}, 200
    
class RecipeResource(Resource) : 
    # path(경로)에 숫자나 문자가 바뀌면서 처리되는 경우에는
    # 해당 변수를, 파라미터에 꼭 써줘야 한다.
    # 이 변수는, app.py 파일의 addResource 함수에서 사용한 변수!
    def get(self, recipe_id) :
        
        print(recipe_id)

        # 1. 클라이언트로부터 데이터를 받아온다.
        #    이미 경로에 들어있는, 레시피 아이디를 받아왔다.
        #    위의 recipe_id라는 변수에 이미 있다.


        # 2. DB에서 레시피 아이디에 해당하는 레시피 1개를 가져온다.
        try :
            connection = get_connection()

            query = '''select *
                        from recipe
                        where id = %s;''' #컬럼 매칭에만 %s
            
            record = (recipe_id,) 
            # 데이터 한개만 있으면 튜플 괄호가 없어짐. 
            # 그래서 뒤에 콤마를 붙여줘야 함.

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            # fetchall 함수는 항상 결과를 리스트로 리턴한다. 
            result_list = cursor.fetchall()

            print('DB에서 결과를 가져온다.')
            print(result_list)

            i = 0
            for row in result_list :
                result_list[i]['created_at']= row['created_at'].isoformat()
                result_list[i]['updated_at']= row['updated_at'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()
        

        except Error as e:
            # pass 였음
            print(e)
            cursor.close()
            connection.close()
            return{"result":"fail", "error":str(e)}, 500

        # 여기서 리스트에 데이터가 있는 경우와 없는 경우로 체크하여
        # 클라이언트에게 데이터를 보낸다.

        # 기존
        # return {'result':'success', 'item': result_list[0]} 

        if len(result_list) == 0 :
            return{"result":"fail","message":"해당 없는 레시피"}, 400
        else :
            return {'result':'success', 'item': result_list[0]} 

    
    def put(self, recipe_id) :

        # 1. 클라이언트로부터 데이터를 받아온다.

        # body 에 들어있는 json 데이터.
        data = request.get_json()

        # 레시피 테이블의 아이디가 저장되어 있는 변수 : recipe_id

        # 2. DB 레시피 테이블을 업데이트 한다.
        try :
            connection = get_connection()

            query = '''update recipe
                        set name = %s, 
                            description = %s,
                            num_of_servings = %s,
                            cook_time = %s,
                            directions = %s
                        where id = %s;'''
            
            record = (data['name'], 
                      data['description'], 
                      data['num_of_servings'], 
                      data['cook_time'], 
                      data['directions'], 
                      recipe_id)
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit() # 반영

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{"result":"fail", "error":str(e)}, 500


        return {"result":"success"},200
    

    ### restful API 에서
    ### GET,DELETE 메소드는 BODY에 JSON데이터를 전달하지 않습니다.
    ### 가능하면 경로에 전달
    ### 안되면 POST 사용?
    def delete(self, recipe_id) :
        
        # 1. 클라이언트로부터 데이터를 받아온다.
        #    이미, recipe_id 받아왔음.

        # 2. 테이블에서 해당 레시피를 삭제한다.
        try :
            connection = get_connection()

            query = '''delete from recipe
                        where id = %s;'''
            
            record =(recipe_id,)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e : 
            print(e)
            cursor.close()
            connection.close()
            return{'result':'fail','error': str(e)}, 500
        
        return{'result':'success'}, 200
    
class RecipePublishResource(Resource) :
    # 하나의 클래스에서 put 함수와 delete 함수로 나눠서 처리하자
    
    def put(self, recipe_id) :
        
        try :
            connection = get_connection()
            query = '''update recipe
                        set is_publish = 1
                        where id = %s;'''
            record = (recipe_id,)
            cursor = connection.cursor()
            cursor.execute(query,record)

            connection.commit()
            cursor.close()
            connection.close()
        except Error as e : 
            print(e)
            cursor.close()
            connection.close()
            return{'result':'fail','error':str(e)}, 500

        return{'result':'success'}, 200
    
    def delete(self, recipe_id) :
        
        try :
            connection = get_connection()
            query = '''update recipe
                        set is_publish = 0
                        where id = %s;'''
            record = (recipe_id,)
            cursor = connection.cursor()
            cursor.execute(query,record)

            connection.commit()
            cursor.close()
            connection.close()
        except Error as e : 
            print(e)
            cursor.close()
            connection.close()
            return{'result':'fail','error':str(e)}, 500

        return{'result':'success'}, 200















