firebase = Firebase()
firebase.ref = firebase.reference("students")
firebase.push("users", {
                    "id": 1,
                    "name": "Luthfi Ganteng",
                    "email": "themightiestemail@gmail.com",
                    "class_id": 1,
                    "password": 12345678,
                    "telp": +6287722582430
                })