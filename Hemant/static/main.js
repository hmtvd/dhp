import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyDDc5E8IgRgtlVutbd0YcMU1oxWlkXZOkM",
    authDomain: "deploy-app-394006.firebaseapp.com",
    projectId: "deploy-app-394006",
    storageBucket: "deploy-app-394006.appspot.com",
    messagingSenderId: "394103822816",
    appId: "1:394103822816:web:259b13e0fdea7944503385",
    measurementId: "G-E8LX03ZZ2S"
  };

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const googleSignInBtn = document.getElementById('google-login-btn');

const provider = new GoogleAuthProvider();
console.log("I wasa executed! before auth")
googleSignInBtn.addEventListener('click', () => {
  signInWithPopup(auth, provider)
    .then((result) => {
      const user = result.user;
      location.replace('/history')
});
});