
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hashtagsteel News Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f4; }
        h1 { text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; }
        th, td { padding: 10px; border: 1px solid #ccc; text-align: left; }
        th { background-color: #003366; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        a { color: #0066cc; text-decoration: none; }
    </style>
</head>
<body>
    <h1>📰 Hashtagsteel News Dashboard</h1>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Title</th>
                <th>Source</th>
                <th>Link</th>
            </tr>
        </thead>
        <tbody>
            {% for item in news %}
            <tr>
                <td>{{ item.Date }}</td>
                <td>{{ item.Title }}</td>
                <td>{{ item.Source }}</td>
                <td><a href="{{ item.Link }}" target="_blank">Read</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
