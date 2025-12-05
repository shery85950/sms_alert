// Initialize Supabase Client
let supabase;

async function initApp() {
    try {
        // Try to fetch configuration from Vercel API
        const response = await fetch('/api/config');

        if (!response.ok) {
            throw new Error('API not available');
        }

        const config = await response.json();

        if (!config.SUPABASE_URL || !config.SUPABASE_ANON_KEY) {
            throw new Error('Missing Supabase configuration');
        }

        supabase = window.supabase.createClient(config.SUPABASE_URL, config.SUPABASE_ANON_KEY);
        console.log('✓ Supabase initialized from Vercel API');

    } catch (error) {
        console.error('API fetch failed:', error.message);

        // Fallback for local development
        // Replace these with your actual values for local testing
        const LOCAL_SUPABASE_URL = 'https://fitvvzylzwmrcnaqvdpl.supabase.co';
        const LOCAL_SUPABASE_ANON_KEY = 'YOUR_ANON_KEY_HERE';

        if (LOCAL_SUPABASE_ANON_KEY === 'YOUR_ANON_KEY_HERE') {
            showMessage('⚠️ Please deploy to Vercel or configure local credentials', 'error');
            document.getElementById('submitBtn').disabled = true;
            return;
        }

        supabase = window.supabase.createClient(LOCAL_SUPABASE_URL, LOCAL_SUPABASE_ANON_KEY);
        console.log('✓ Supabase initialized from local config');
    }
}

// Call initialization
initApp();

document.getElementById('signupForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    if (!supabase) {
        showMessage('System not initialized. Please refresh.', 'error');
        return;
    }

    const submitBtn = document.getElementById('submitBtn');
    const messageDiv = document.getElementById('message');
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    // Basic Validation
    if (!data.name || !data.phone || !data.station) {
        showMessage('Please fill in all fields.', 'error');
        return;
    }

    // Disable button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Signing up...';
    messageDiv.textContent = '';
    messageDiv.className = 'message';

    try {
        // Insert data into 'users' table
        const { error } = await supabase
            .from('users')
            .insert([
                { name: data.name, phone: data.phone, station: data.station }
            ]);

        if (error) {
            console.error('Supabase Error:', error);
            if (error.code === '23505') { // Unique violation
                showMessage('This phone number is already registered.', 'error');
            } else {
                showMessage('Error saving data. Please try again.', 'error');
            }
        } else {
            showMessage('Successfully signed up for alerts!', 'success');
            this.reset();
        }
    } catch (err) {
        console.error('Unexpected Error:', err);
        showMessage('An unexpected error occurred.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign Up for Alerts';
    }
});

function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
}
