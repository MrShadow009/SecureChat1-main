from flask import Flask, render_template, request, jsonify
from passlib.hash import pbkdf2_sha256
import uuid

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = 'replace-with-a-secure-secret'

# In-memory room store
rooms = {}

@app.route('/')
def index():
    return render_template('index_socketio.html')

# Create a room
@app.route('/api/create-room', methods=['POST'])
def create_room():
    data = request.json or {}
    room_name = data.get('room_name')
    algorithm = data.get('algorithm', 'RSA')
    passphrase = data.get('passphrase')
    creator = data.get('creator', 'unknown')

    if not room_name or not passphrase:
        return jsonify({'error': 'room_name and passphrase required'}), 400

    room_id = str(uuid.uuid4())
    pass_hash = pbkdf2_sha256.hash(passphrase)
    rooms[room_id] = {
        'name': room_name,
        'algorithm': algorithm,
        'pass_hash': pass_hash,
        'creator': creator,
        'participants': {},
        'messages': [],
        'next_message_id': 0
    }
    return jsonify({'room_id': room_id, 'message': 'room created', 'algorithm': algorithm})

# Join room
@app.route('/api/join-room', methods=['POST'])
def join_room_http():
    data = request.json or {}
    room_id = data.get('room_id')
    passphrase = data.get('passphrase')
    username = data.get('username') or 'guest'

    room = rooms.get(room_id)
    if not room:
        return jsonify({'error': 'room not found'}), 404

    if not pbkdf2_sha256.verify(passphrase, room['pass_hash']):
        return jsonify({'error': 'invalid passphrase'}), 403

    if username not in room['participants']:
        room['participants'][username] = True
    
    return jsonify({
        'room_id': room_id, 
        'message': 'ok', 
        'algorithm': room['algorithm'], 
        'creator': room['creator'], 
        'room_name': room['name']
    })

# Delete room
@app.route('/api/delete-room', methods=['POST'])
def delete_room():
    data = request.json or {}
    room_id = data.get('room_id')
    username = data.get('username')

    room = rooms.get(room_id)
    if not room:
        return jsonify({'error': 'room not found'}), 404

    if room['creator'] != username:
        return jsonify({'error': 'Only the room creator can delete this room'}), 403

    del rooms[room_id]
    return jsonify({'success': True, 'message': 'Room deleted'})

# Send message
@app.route('/api/send-message', methods=['POST'])
def send_message():
    data = request.json or {}
    room_id = data.get('room_id')
    username = data.get('username')
    message = data.get('message')
    
    room = rooms.get(room_id)
    if not room or username not in room['participants']:
        return jsonify({'error': 'unauthorized'}), 403
    
    msg_id = room['next_message_id']
    room['next_message_id'] += 1
    room['messages'].append({'id': msg_id, 'username': username, 'message': message})
    
    return jsonify({'success': True})

# Get messages
@app.route('/api/get-messages', methods=['GET'])
def get_messages():
    room_id = request.args.get('room_id')
    room = rooms.get(room_id)
    
    if not room:
        return jsonify({'error': 'room not found'}), 404
    return jsonify({'messages': room['messages'], 'next_id': room['next_message_id']})

# Get participants
@app.route('/api/get-participants', methods=['GET'])
def get_participants():
    room_id = request.args.get('room_id')
    room = rooms.get(room_id)
    
    if not room:
        return jsonify({'error': 'room not found'}), 404
    
    participants = []
    for p in room['participants']:
        participant = {'username': p}
        if p == room['creator']:
            participant['is_admin'] = True
        participants.append(participant)
    
    return jsonify({'participants': participants, 'creator': room['creator']})

# Leave room
@app.route('/api/leave-room', methods=['POST'])
def leave_room():
    data = request.json or {}
    room_id = data.get('room_id')
    username = data.get('username')
    
    room = rooms.get(room_id)
    if room and username in room['participants']:
        del room['participants'][username]
    
    return jsonify({'success': True})

# Get all rooms
@app.route('/api/get-rooms', methods=['GET'])
def get_rooms_endpoint():
    room_list = []
    for room_id, room in rooms.items():
        room_list.append({
            'room_id': room_id,
            'name': room['name'],
            'algorithm': room['algorithm'],
            'participant_count': len(room['participants']),
            'creator': room['creator']
        })
    return jsonify({'rooms': room_list})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
