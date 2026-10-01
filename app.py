from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, get_db_connection

app = Flask(__name__)
CORS(app)

# Пересоздаем таблицы при запуске приложения
init_db()


@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Получение списка заметок с фильтрацией, пагинацией и JOIN."""
    conn = get_db_connection()
    
    # Читаем параметры фильтрации и пагинации из адресной строки URL
    category_id = request.args.get('category_id', type=int)
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=5, type=int)
    
    # Считаем отступ для пагинации (какие записи пропускать)
    offset = (page - 1) * limit

    # Базовый SQL-запрос с объединением таблиц (JOIN)
    # Вытаскиваем название категории из таблицы categories
    query = """
        SELECT notes.id, notes.title, notes.content, notes.created_at, categories.name AS category_name
        FROM notes
        LEFT JOIN categories ON notes.category_id = categories.id
    """
    params = []

    # Добавляем фильтрацию по категории, если параметр передан в URL
    if category_id is not None:
        query += " WHERE notes.category_id = ?"
        params.append(category_id)

    # Добавляем сортировку, лимит и отступ для пагинации
    query += " ORDER BY notes.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    db_notes = conn.execute(query, params).fetchall()
    conn.close()
    
    # Формируем JSON ответ
    notes_list = []
    for row in db_notes:
        notes_list.append({
            "id": row["id"],
            "title": row["title"],
            "content": row["content"],
            "category_name": row["category_name"] or "Без категории",
            "created_at": row["created_at"]
        })
        
    return jsonify({
        "page": page,
        "limit": limit,
        "data": notes_list
    }), 200


@app.route('/api/notes', methods=['POST'])
def create_note():
    """Создание заметки с привязкой к категории."""
    data = request.get_json() or {}
    
    if 'title' not in data or 'content' not in data:
        return jsonify({"error": "Заголовок и текст обязательны"}), 400
        
    title = data['title'].strip()
    content = data['content'].strip()
    category_id = data.get('category_id') # Может быть None, если категорию не выбрали

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO notes (title, content, category_id) VALUES (?, ?, ?)', 
            (title, content, category_id)
        )
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # Сработает, если передали несуществующий ID категории
        return jsonify({"error": "Указанной категории не существует"}), 400
    finally:
        conn.close()
        
    return jsonify({"message": "Заметка успешно сохранена", "note_id": new_id}), 201


# Дополнительный эндпоинт, чтобы в Postman можно было посмотреть список доступных категорий
@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    db_cats = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "name": r["name"]} for r in db_cats]), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
