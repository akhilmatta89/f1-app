import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, 
         GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDFKQW0iWSOV73S8AdgRb3l3eFV9SDutMY",
  authDomain: "flask-demo-25680.firebaseapp.com",
  projectId: "flask-demo-25680",
  storageBucket: "flask-demo-25680.firebasestorage.app",
  messagingSenderId: "30541412826",
  appId: "1:30541412826:web:e667c2b8064312880ae8e3",
  measurementId: "G-WX75N6H7Q5"
};

  // Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const db = getFirestore(app);

export { auth, provider, db };