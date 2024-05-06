from flask import Flask, render_template, request, redirect, url_for, session
import folium
import requests
from folium.plugins import AntPath

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

class CollegeNavigator:
    def __init__(self, repository_url):
        self.repository_url = repository_url
        self.geoResources = {}
        self.college_map = None
        self.fetchGeoJSONFiles()

    def fetchGeoJSONFiles(self):
        response = requests.get(self.repository_url)
        files_data = response.json()
        for file in files_data:
            if file['name'].endswith('.geojson'):
                self.geoResources[file['name'].split('.')[0]] = file['download_url']

    def displayMap(self, path_name):
        if self.college_map is None:
            self.college_map = folium.Map(location=[9.950585500478837, 76.63085559957005], zoom_start=17)
        else:
            self.college_map = folium.Map(location=[9.950585500478837, 76.63085559957005], zoom_start=17)

        path_url = self.geoResources.get(path_name)
        if path_url is None:
            return "Path not found."

        path_data = requests.get(path_url).json()
        try:
            features = path_data['features']
            for feature in features:
                geometry_type = feature['geometry']['type']
                properties = feature['properties']
                coordinates = feature['geometry']['coordinates']
                if geometry_type == 'Point':
                    self.addMarker(coordinates, properties)
                elif geometry_type == 'Polygon':
                    self.addPolygon(coordinates, properties)
                elif geometry_type == 'MultiLineString':
                    self.addMultiLineString(coordinates, properties)
                elif geometry_type == 'LineString':
                    self.addLineString(coordinates, properties)
            map_path = self.college_map._repr_html_()

            # Additional information to display
            if path_name == "ABlock1" or path_name == "ABlock2":
                information = {
                    "Toilet (Gents) - A-101 ": "Ground Floor",
                    "Faculty Room IT 1 - A-102 ": "Ground Floor",
                    "Faculty Room IT 2 - A-203 ": "First Floor",
                    "Hardware Re Lab CSE - A-204 ": "First Floor",
                    "Multimedia Lab - A-302 Second Floor": "Second Floor",
                    "Network System Lab - A-304 ": "Second Floor"
                }

                info_html = "<h2>Additional Information:</h2>"
                info_html += "<ul>"
                for key, value in information.items():
                    info_html += f"<li>{key}: {value}</li>"
                info_html += "</ul>"

                # Combine map HTML and additional information HTML
                combined_html = f"{map_path}{info_html}"
            else:
                combined_html = map_path

            return combined_html
        except (KeyError, IndexError):
            return "Error: Unable to extract features from GeoJSON data."

    def addMarker(self, coordinates, properties):
        marker = folium.Marker(location=[coordinates[1], coordinates[0]], popup=str(properties))
        marker.add_to(self.college_map)

    def addPolygon(self, coordinates, properties):
        polygon = folium.Polygon(locations=[[point[1], point[0]] for point in coordinates[0]], color='blue', fill=True, fill_color='blue', fill_opacity=0.4, popup=str(properties))
        polygon.add_to(self.college_map)

    def addMultiLineString(self, coordinates, properties):
        for line_coordinates in coordinates:
            ant_path = AntPath(locations=[[point[1], point[0]] for point in line_coordinates], color='red', weight=5, popup=str(properties))
            ant_path.add_to(self.college_map)

    def addLineString(self, coordinates, properties):
        ant_path = AntPath(locations=[[point[1], point[0]] for point in coordinates], color='green', weight=5, popup=str(properties))
        ant_path.add_to(self.college_map)

myCollegeNavigator = CollegeNavigator("https://api.github.com/repos/Alpha-Deivam/College/contents/Paths")

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username and password are correct
        if username == 'teacher' and password == 'teacher':
            session['logged_in'] = True
            return redirect(url_for('teacher_index'))  # Redirect to the index page after successful login
        elif username == 'student' and password == 'student':
            session['logged_in'] = True
            return redirect(url_for('student_index'))  # Redirect to the index page after successful login
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))  # Redirect to the login page after logout

# Protect routes requiring authentication
@app.route('/teacher_index')
def teacher_index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))  # Redirect to the login page if not logged in
    
    # Customize the names for display
    paths = {}
    for key, _ in myCollegeNavigator.geoResources.items():
        if key.endswith("1"):
            display_name = key[:-1] + " Gate 1"
        elif key.endswith("2"):
            display_name = key[:-1] + " Gate 2"
        else:
            display_name = key  # Keep the original name if it doesn't end with "1" or "2"
        paths[key] = display_name
    return render_template('teacher_index.html', paths=paths)

@app.route('/')
def student_index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))  # Redirect to the login page if not logged in
    
    # Customize the names for display
    paths = {}
    for key, _ in myCollegeNavigator.geoResources.items():
        if key.endswith("1"):
            display_name = key[:-1] + " Gate 1"
        elif key.endswith("2"):
            display_name = key[:-1] + " Gate 2"
        else:
            display_name = key  # Keep the original name if it doesn't end with "1" or "2"
        paths[key] = display_name
    return render_template('student_index.html', paths=paths)

@app.route('/display_map', methods=['POST'])
def display_map():
    if 'logged_in' not in session:
        return redirect(url_for('login'))  # Redirect to the login page if not logged in
    
    path_name = request.form['path_name']
    map_html = myCollegeNavigator.displayMap(path_name)
    return render_template('display_map.html', map_html=map_html)

if __name__ == '__main__':
    app.run(debug=False)
