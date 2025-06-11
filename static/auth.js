// Load Supabase JS library if not already loaded
if (!window.supabase) {
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js";
    script.onload = initializeSupabase;
    document.head.appendChild(script);
  } else {
    initializeSupabase();
  }
  
  // Initialize Supabase using configuration from the server
  function initializeSupabase() {
    fetch("/config")
      .then(response => response.json())
      .then(config => {
        if (!config.SUPABASE_URL || !config.SUPABASE_KEY) {
          throw new Error("Missing Supabase config");
        }
        window.supabase = supabase.createClient(config.SUPABASE_URL, config.SUPABASE_KEY);
        console.log("Supabase initialized:", config.SUPABASE_URL);
      })
      .catch(error => console.error("Error fetching config:", error));
  }
  
  // Wait until Supabase is initialized
  async function waitForSupabase() {
    while (!window.supabase) {
      await new Promise(resolve => setTimeout(resolve, 100)); // Wait 100ms
    }
  }
  
  // Sign up function for new users
  async function signUp() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const name = document.getElementById("name").value.trim();
  const phoneno = document.getElementById("phone").value.trim();

  if (!username || !password || !name || !phoneno) {
    alert("All fields are required!");
    return;
  }

   const { data, error } = await supabase
    .from("users")
    .insert([{ username, password, name, phoneno }]);

  if (error) {
    alert("Sign-up failed: " + error.message);
  } else {
    alert("User registered!");
    window.location.href = "login.html";
  }
}

  
  // Login function for existing users
  async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username || !password) {
    alert("Please enter both username and password.");
    return;
  }

  // Query the users table for matching username and password
  const { data, error } = await supabase
    .from("users")
    .select("*")
    .eq("username", username)
    .eq("password", password);
    

  if (error) {
    alert("Invalid credentials. Please try again.");
    console.error("Login failed:", error?.message || "No matching user found.");
  } else {
    alert("Login successful!");
    window.location.href = "sel_page.html";
  }
}

  
  // Expose functions to the global scope
  window.signUp = signUp;
  window.login = login;
  