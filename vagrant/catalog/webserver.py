from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer 


class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header("Content-type","text/html")
				self.end_headers()

				output = ""
				output += "<html><body>HELLO!</body></html>"
				self.wfile.write(output)
				print output
				return
		except IOError:
			self.send_error(404, "File Not Found %s" %self.path)


def main():
	try:
		port = 8080
		server = HTTPServer(("",port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt as e:
		print "\nProcess interupted by keyboard",str(e)

if __name__ == "__main__":
	main()