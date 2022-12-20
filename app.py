import random
from flask import Flask, request, jsonify
from flask_pydantic_spec import (
    FlaskPydanticSpec, Response, Request
)
from tinydb import Query, where
from tinydb.operations import increment
from api.model.modelMessage import MessageOut, MessageIn
from api.model.modelMessagesList import Messages
from api.model.ModelQuery import QueryMessage
from api.schema.database import database

server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='RestStone')
spec.register(server)


@server.get('/messages') 
@spec.validate(
    query=QueryMessage,
    resp=Response(HTTP_200=Messages)
)
def SearchAllMessages():
    """Return all Messages."""
    query = request.context.query.dict(exclude_none=True)
    all_mensages = database.search(
        Query().fragment(query)
    )
    return jsonify(
        Messages(
            Messages=all_mensages,
            count=len(all_mensages)
        ).dict()
    )

@server.get('/messages/<int:id>')
@spec.validate(resp=Response(HTTP_200=MessageOut))
def SearchMessagesById(id):
    """Get All Messages by Id."""
    try:
        Message = database.search(Query().id == id)[0]
    except IndexError:
        return {'message': 'Message not found!'}, 404
    return jsonify(Message)


@server.get('/messages/random/<int:votes>')
@spec.validate(resp=Response(HTTP_200=MessageOut))
def SearchMessagesByVotes(votes):
    """Get random messages with a minimum of votes."""
    try:
        Message = database.search(Query().votes >= votes)
        chosed_message = Message[random.randrange(len(Message))]
    except ValueError:
        return {'message': 'There are NO Messages with these number of Votes!'}, 404
    return jsonify(chosed_message)
        

@server.post('/messages')
@spec.validate(
    body=Request(MessageIn), resp=Response(HTTP_201=MessageIn)
)
def InsertMessage():
    """Add an Message ."""
    count = database.all()
    if(database.search(Query().text == request.context.body.text)):
        return {'message': 'Message alredy exists!'}, 402
    body = request.context.body.dict()
    body['id'] = len(count)
    body['votes'] = 0
    database.insert(body)
    return body


@server.put('/messages/<int:id>')
@spec.validate(
    body=Request(MessageIn), resp=Response(HTTP_201=MessageOut)
)
def UpdateMessage(id):
    """Alter an Message in Database."""
    Message = Query()
    body = request.context.body.dict()
    database.update(body, Message.id == id)
    return jsonify(body)


@server.delete('/messages/<int:id>')
@spec.validate(resp=Response('HTTP_204'))
def DeleteMessage(id):
    """Remove an Message of Database."""
    database.remove(Query().id == id)
    return jsonify({})

@server.patch('/messages/<int:id>')
@spec.validate(

)
def Vote(id):
    """Vote for the Message."""
    Messages = database.search(Query().id == id)
    if(len(Messages) > 0): 
        database.update(increment("votes"), where('id') == id  )
        return {'message': 'successful vote!'}, 200 
    else:
        return {'message': 'message not found'}, 404 

server.run(host="0.0.0.0",port=1234 , debug=True)