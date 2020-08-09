from flask import Flask, jsonify, request, session
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

Data = []


class Application(Resource):
    def __init__(self):
        pass

    def get(self, name):
        for x in Data:
            if x['Data'] == name:
                return x
        return jsonify(session["todo"])
        return {'Data': None}

    def post(self, name):
        Tem = {'Data': name}
        Data.append(Tem)
        return Tem

    def delete(self, name):
        for ind, x in enumerate(Data):
            if x['Data'] == name:
                Tem = Data.pop(ind)
                return {'Note': 'Deleted'}

# route http posts to this method
@app.route('/api/test', methods=['POST'])
def test():
    r = request
    # convert string of image data to uint8
    nparr = np.fromstring(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # do some fancy processing here....

    # build a response dict to send back to client
    response = {'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0])
                }
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")

import io
from flask import send_file

@app.route("/send_file")
def send_file():
    file = io.BytesIO()
    file.write(b"Hello, World!")
    file.seek(0)
    return send_file(file, attachment_filename=f"example.txt", as_attachment=True)

api.add_resource(Application, '/Name/<string:name>')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
