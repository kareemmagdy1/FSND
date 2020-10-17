from flask import Flask, jsonify, redirect
import sys, os
sys.path.insert(0, os.path.abspath('..'))
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Question, Category,db
import json
QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    app=Flask(__name__)
    setup_db(app)
    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/')
    def hello():
        return jsonify({'message': 'yo'})

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/data/api/categories', methods=['GET'])
    def get_requests():
        categories=db.session.query(Category).all()
        categoriesData=[]
        for category in categories:
            categoriesData.append(category.type)
        return jsonify({
            'categories':categoriesData})

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
    '''
    @app.route('/data/api/questions/')
    def get_questions():
        pageNumber=int(request.args.get('page'))
        pageNumber-=1
        questions=db.session.query(Question).all()
        categories = db.session.query(Category).all()

        totalQuestions=len(questions)
        print(totalQuestions)

        start=pageNumber * QUESTIONS_PER_PAGE
        end=start+QUESTIONS_PER_PAGE
        questions=questions[start:end]
        if (len(questions) == 0):
            abort(404)

        questionsData=[]
        for question in questions:
            questionsData.append({
                'question':question.question,
                'category':question.category,
                'difficulty':question.difficulty,
                'answer':question.answer,
                'id':question.id
            })
        categoriesData = []
        for category in categories:
            # categoriesData.append({
            #     'type':category.type,
            #     'id':category.id
            # })
            categoriesData.append(category.type)

        currentCategory=categoriesData[0]
        print(len(categoriesData))
        for data in categoriesData:
            print(data)
        return jsonify({
            'currentCategory':currentCategory,
            'categories':categoriesData,
            'totalQuestions':totalQuestions,
            'questions':questionsData
        })

    '''
       @TODO: 
       Create an endpoint to DELETE question using a question ID. 

       TEST: When you click the trash icon next to a question, the question will be removed.
       This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/question/api/<int:id>',methods=['DELETE'])
    def delete_question(id):
        try:
            object = db.session.query(Question).filter(Question.id == id).first()
            db.session.delete(object)
            db.session.commit()
            return jsonify({
                'success':True
            })
        except:
            db.session.rollback()
            abort(400)
        finally:
            db.session.close()

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/data/api/question',methods=['POST'])
    def create_question():
        data=json.loads(request.get_data())
        try:
            category_type=db.session.query(Category.type).filter(Category.id==int(data['category'])).first()
            question=Question(answer=data['answer'],question=data['question'],difficulty=int(data['difficulty']),
                              category=category_type)
            question.insert()
            selection=Question.query.order_by(Question.id).all
            return jsonify({
                'success':True,
                'created':question.id
            })
        except:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
            return jsonify({
                'success':False
            })

    '''
       @TODO: 
       Create a POST endpoint to get questions based on a search term. 
       It should return any questions for whom the search term 
       is a substring of the question. 

       TEST: Search by any phrase. The questions list will update to include 
       only question that include that string within their question. 
       Try using the word "title" to start. 
    '''
    @app.route('/question/api/find/',methods=['POST'])
    def find_question():
        searchTerm = request.args.get('term')
        questions=db.session.query(Question).filter(Question.question.like('%' +searchTerm + '%')).all()
        questionsData=[]
        for q in questions:
            questionsData.append(q.format())
        totalQuestions=len(questionsData)
        currentCategory=db.session.query(Category.type).first()
        return jsonify({
        'totalQuestions':totalQuestions,
        'questions':questionsData,
        'currentCategory':currentCategory
        })


    '''
   @TODO: 
   Create a GET endpoint to get questions based on category. 

   TEST: In the "List" tab / main screen, clicking on one of the 
   categories in the left column will cause only questions of that 
   category to be shown. 
   '''
    @app.route('/categories/<int:categoryId>/questions')
    def get_questions_by_category(categoryId):
        categoryId+=1
        category=db.session.query(Category.type).filter(Category.id==categoryId).first()
        questions=db.session.query(Question).filter(Question.category==category).all()
        questionsData=[]
        for q in questions:
            questionsData.append(q.format())
        totalQuestions=len(questions)
        currentCategory=db.session.query(Category.type).first()
        return jsonify({
            'questions': questionsData,
            'totalQuestions': totalQuestions,
            'currentCategory': currentCategory
        })

    '''
       @TODO: 
       Create a POST endpoint to get questions to play the quiz. 
       This endpoint should take category and previous question parameters 
       and return a random questions within the given category, 
       if provided, and that is not one of the previous questions. 

       TEST: In the "Play" tab, after a user selects "All" or a category,
       one question at a time is displayed, the user is allowed to answer
       and shown whether they were correct or not. 
       '''
    @app.route('/play/api/questions',methods=['POST'])
    def get_next_question():
        data = json.loads(request.get_data())
        previousQuestion=data['previous_questions']
        category=data['quiz_category']
        filters=[]
        if(category['type']=='click'):
            if (len(previousQuestion) == 0):
                choosenQuestion = db.session.query(Question).first()
                return jsonify({
                    'question': choosenQuestion.format()
                })
            else:
                index = len(previousQuestion) - 1
                newQuestion = db.session.query(Question).filter(Question.id > previousQuestion[index]).first()
                if (newQuestion == None):
                    return jsonify({
                        'question': None
                    })
                return jsonify({
                    'question': newQuestion.format()
                })
        else:
            if(len(previousQuestion)==0):
                choosenQuestion=db.session.query(Question).filter(category['type']==Question.category).first()
                return jsonify({
                    'question':choosenQuestion.format()
                })
            else:
                index=len(previousQuestion)-1
                newQuestion=db.session.query(Question).filter(category['type']==Question.category,Question.id>previousQuestion[index]).first()
                if(newQuestion==None):
                    return jsonify({
                        'question':None
                    })
                return jsonify({
                    'question':newQuestion.format()
                })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':404,
            'message':'Not Found'
        }),404
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':400,
            'message':'bad request'
        }),400
    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':422,
            'message':'unprocessable'
        }),422
    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':500,
            'message':'Internal Server Error'
        }),500

    return app
