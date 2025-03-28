fetch("/config")
  .then(response => response.json())
  .then(config => {
      const SUPABASE_URL = config.SUPABASE_URL;
      const SUPABASE_KEY = config.SUPABASE_KEY;

      const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

      console.log("Supabase initialized:", SUPABASE_URL);
  })
  .catch(error => console.error("Error fetching config:", error));


const supabaseUrl = "https://cmunvjxgxvkorvzccrec.supabase.co"; 
const supabaseAnonKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtdW52anhneHZrb3J2emNjcmVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE4ODQxMDYsImV4cCI6MjA1NzQ2MDEwNn0.nr-HQzF529rqoKu1-y-28zX-iYGp-glcatmMG2xPQog"; // Replace with your Supabase anon key

const supabase =window. supabase.createClient(supabaseUrl, supabaseAnonKey);


async function signUp() {
    
    const username = document.getElementById("username")?.value.trim();
    const name = document.getElementById("name")?.value.trim();
    const phoneno = document.getElementById("phone")?.value.trim();
    const password = document.getElementById("password")?.value;
    const confirmPassword = document.getElementById("confirm-password")?.value;

    console.log(username, name, phoneno, password, confirmPassword);
    if (!username || !name || !phoneno || !password || !confirmPassword) {
        alert("Please fill out all fields!");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    const { data, error } = await supabase.auth.signUp({
        email: username + "@example.com", 
        password: password
    });

    if (error) {
        console.error("Sign-up error:", error.message);
        alert("Error signing up: " + error.message);
        return;
    }

    const user = data.user;
    if (user) {
        const { error: dbError } = await supabase
            .from("users")
            .insert([
                {
                    id: user.id,  
                    username: username,
                    name: name,
                    phoneno: phoneno,
                    password: password 
                }
            ]);

        if (dbError) {
            console.error("Database insert error:", dbError.message);
            alert("Error saving user details: " + dbError.message);
            return;
        }

        alert("Sign-up successful! Redirecting to login.");
        window.location.href = "login.html";
    }
}



async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const { user, error } = await supabase.auth.signInWithPassword({
        email: username + "@example.com",
        password: password
    });

    if (error) {
        console.error("Login error:", error.message);
        alert("Error logging in: " + error.message);
    } else {
        alert("Login successful!");
        window.location.href = "dashboard.html"; 
    }
}


async function logout() {
    const { error } = await supabase.auth.signOut();

    if (error) {
        console.error("Logout error:", error.message);
        alert("Error logging out: " + error.message);
    } else {
        alert("Logged out successfully!");
        window.location.href = "login.html"; 
    }
}
