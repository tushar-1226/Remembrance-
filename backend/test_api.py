import urllib.request
import json

BASE_URL = "http://localhost:8000/api"

def make_request(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
        json_data = json.dumps(data).encode("utf-8")
        req.data = json_data
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Request to {url} failed: {e}")
        return 500, None

def run_tests():
    print("--- Running API Endpoint Tests ---")
    
    # 1. Create a note
    note_payload = {
        "title": "Test FastAPI Note",
        "content": "Writing a next js note with react",
        "category": "structured",
        "font_style": "mono"
    }
    status, note = make_request(f"{BASE_URL}/notes", "POST", note_payload)
    print(f"Create Note: Status {status}, Title: '{note['title']}', ID: {note['id']}")
    assert status == 200
    assert note["title"] == "Test FastAPI Note"
    note_id = note["id"]

    # 2. Get the note
    status, fetched_note = make_request(f"{BASE_URL}/notes/{note_id}", "GET")
    print(f"Get Note: Status {status}, Title: '{fetched_note['title']}'")
    assert status == 200
    assert fetched_note["id"] == note_id

    # 3. Update the note
    update_payload = {
        "title": "Updated Test Note",
        "content": "Let's learn python fastapi"
    }
    status, updated_note = make_request(f"{BASE_URL}/notes/{note_id}", "PUT", update_payload)
    print(f"Update Note: Status {status}, Title: '{updated_note['title']}', Content: '{updated_note['content']}'")
    assert status == 200
    assert updated_note["title"] == "Updated Test Note"

    # 4. Review the note (SM-2 Quality 4)
    status, reviewed_note = make_request(f"{BASE_URL}/notes/{note_id}/review", "POST", {"quality": 4})
    print(f"Review Note (SM-2): Status {status}, Interval: {reviewed_note['review_interval']}, Repetitions: {reviewed_note['repetitions']}, Ease: {reviewed_note['ease_factor']}")
    assert status == 200
    assert reviewed_note["repetitions"] == 1
    assert reviewed_note["review_interval"] == 1

    # 5. Review the note again (SM-2 Quality 5)
    status, reviewed_note_2 = make_request(f"{BASE_URL}/notes/{note_id}/review", "POST", {"quality": 5})
    print(f"Review Note 2 (SM-2): Status {status}, Interval: {reviewed_note_2['review_interval']}, Repetitions: {reviewed_note_2['repetitions']}, Ease: {reviewed_note_2['ease_factor']}")
    assert status == 200
    assert reviewed_note_2["repetitions"] == 2
    assert reviewed_note_2["review_interval"] == 6

    # 6. Get Canvas State
    status, canvas = make_request(f"{BASE_URL}/canvas", "GET")
    print(f"Get Canvas State: Status {status}, ID: {canvas['id']}")
    assert status == 200

    # 7. Update Canvas State
    canvas_payload = {
        "data": '{"paths": [{"x": 10, "y": 20}], "stickies": [{"id": 123, "text": "Hello canvas", "x": 100, "y": 100, "color": "yellow"}]}'
    }
    status, updated_canvas = make_request(f"{BASE_URL}/canvas", "POST", canvas_payload)
    print(f"Save Canvas State: Status {status}, Data Length: {len(updated_canvas['data'])}")
    assert status == 200

    # 8. Delete the note
    status, msg = make_request(f"{BASE_URL}/notes/{note_id}", "DELETE")
    print(f"Delete Note: Status {status}, Msg: {msg['message']}")
    assert status == 200

    print("--- All API Tests Passed Successfully! ---")

if __name__ == "__main__":
    run_tests()
