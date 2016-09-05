from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine("sqlite:///restaurantmenu.db")

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("/hello"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += """
            <html>
                <body>
                    <h1>Hello!</h1>

                    <form method="POST" enctype="multipart/form-data" action="/hello">
                        <h2>What would you like me to say?</h2>
                        <input name="message" type="text">
                        <input type="submit" value="Submit">
                    </form>
                </body>
            </html>
            """
            self.wfile.write(message)
            # print message
            return
        elif self.path.endswith("/hola"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += """
            <html>
                <body>
                    <h1>&#161Hola!</h1>
                    <a href="/hello">Back to Hello</a>

                    <form method="POST" enctype="multipart/form-data" action="/hello">
                        <h2>What would you like me to say?</h2>
                        <input name="message" type="text">
                        <input type="submit" value="Submit">
                    </form>
                </body>
            </html>
            """
            self.wfile.write(message)
            # print message
            return
        elif self.path.endswith("/restaurants"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += """
            <html>
                <body>
                    <h1>Here are the restaurants</h1>
                    <a href="/hello">Back to Hello</a>
                    <a href="{}/new">Create New Restaurant?</a>
            """.format("/restaurants")
            for i in session.query(Restaurant).all():
                message += """
                <p style='marin-bottom=0;'>%(name)s</p>
                <a href="%(edit)s">Edit</a>
                <br>
                <a href="%(delete)s">Delete</a>
                <br>
                <br>
                """ % {
                "name":i.name,
                "edit": self.path+"/{}".format(i.id)+"/edit",
                "delete": self.path+"/{}".format(i.id)
                }

            message += """
                </body>
            </html>
            """
            self.wfile.write(message)
            # print message
            return
        elif self.path.endswith("/new"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += """
            <html>
                <body>
                    <h1>Create a new Restaurant!</h1>
                    <a href="/hello">Back to Hello</a>
                    <a href="/hola">Back to Hola</a>

                    <form method="POST" enctype="multipart/form-data" action="/restaurants">
                        <h2>What would you like to call your Restaurant?</h2>
                        <input name="rest_name" type="text">
                        <input type="submit" value="Submit">
                    </form>
                </body>
            </html>
            """
            self.wfile.write(message)
            # print message
            return
        elif self.path.endswith("/edit"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += """
            <html>
                <body>
                    <h1>Create a new Restaurant!</h1>
                    <a href="/hello">Back to Hello</a>
                    <a href="/hola">Back to Hola</a>
                    <a href="/restaurants">Restaurants</a>
                    <a href="/restaurants/new">Create Restaurant</a>

                    <form method="POST" enctype="multipart/form-data" action="/restaurants">
                        <h2>What would you like to rename your Restaurant?</h2>
                        <input name="rest_name" type="text">
                        <input type="submit" value="Submit">
                    </form>
                </body>
            </html>
            """
            self.wfile.write(message)
            # print message
            return
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if self.path.endswith('/restaurants/new'):
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
                rest_names = fields.get("rest_name")

            myFirstRestaurant = Restaurant(name=rest_names[0])
            session.add(myFirstRestaurant)
            session.commit()

            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()

        elif self.path.endswith('/edit'):
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
                rest_names = fields.get("rest_name")

            idx = int( re.findall("ants/(\d+)/edit", self.path) )
            some_restaurant = Restaurant(id=idx)
            some_restaurant = session.query(Restaurant).filter_by(id=idx).one()
            some_restaurant.name = rest_names[0]
            session.add(some_restaurant)
            session.commit()

            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()