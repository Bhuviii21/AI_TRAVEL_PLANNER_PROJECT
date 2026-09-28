from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import markdown
from utils.llm import generate_itinerary
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ---------------- LANGUAGE SUPPORT ----------------

LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'ja': 'Japanese',
    'zh': 'Chinese'
}

# Complete translations for all languages
TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome',
        'plan_dream': 'Plan Your Dream Journey with AI',
        'discover_destinations': 'Discover destinations, generate personalized itineraries, estimate budgets, and travel smarter with Artificial Intelligence.',
        'popular_destinations': 'Popular Destinations',
        'explore_destinations': 'Explore the most loved destinations around the world',
        'generate_trip': 'Generate AI Trip',
        'destination': 'Destination',
        'days': 'Days',
        'budget': 'Budget (₹)',
        'travelers': 'Travelers',
        'style': 'Travel Style',
        'interests': 'Interests (comma separated)',
        'saved_trips': 'My Saved Trips',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'dashboard': 'Dashboard',
        'home': 'Home',
        'no_trips': 'No trips found',
        'generate_first': 'Generate Your First Trip',
        'welcome_back': 'Welcome back',
        'language': 'Language',
        'my_trips': 'My Trips',
        'total_trips': 'Total Trips',
        'destinations': 'Destinations',
        'total_budget': 'Total Budget',
        'max_budget': 'Max Budget (₹)',
        'destination_filter': 'Destination',
        'search_destination': 'Search destination...',
        'sort_by': 'Sort By',
        'newest': 'Newest',
        'oldest': 'Oldest',
        'budget_high': 'Budget: High-Low',
        'budget_low': 'Budget: Low-High',
        'apply_filters': 'Apply Filters',
        'clear': 'Clear',
        'days_short': 'days',
        'actions': 'Actions',
        'view': 'View',
        'delete': 'Delete',
        'no_preview': 'No preview available',
        'no_trips_match': 'No trips match your filters. Try adjusting your search criteria.',
        'no_trips_yet': "You haven't planned any trips yet. Start your adventure now!",
        'login_title': 'Login to your AI Travel Planner account',
        'email': 'Email Address',
        'password': 'Password',
        'enter_email': 'Enter your email',
        'enter_password': 'Enter your password',
        'no_account': "Don't have an account?",
        'create_account': 'Create Account',
        'back_home': '← Back to Home',
        'register_title': 'Start planning your dream journey with AI',
        'full_name': 'Full Name',
        'enter_name': 'Enter your full name',
        'create_password': 'Create a password (min 6 characters)',
        'confirm_password': 'Confirm Password',
        'confirm_password_placeholder': 'Confirm your password',
        'already_account': 'Already have an account?',
        'weak_password': 'Weak password',
        'medium_password': 'Medium password',
        'strong_password': 'Strong password',
        'trip_plan': 'Your Trip Plan',
        'destination_label': 'Destination:',
        'your_budget': 'Your Budget',
        'trip_generated': '✅ Trip generated within your specified budget',
        'view_all_trips': '📋 View All Trips',
        'plan_another': '✈ Plan Another Trip',
        'back_to_dashboard': '← Back to Dashboard',
        'location_map': '📍 Location Map',
        'open_in_map': '🌍 Open in OpenStreetMap',
        'no_location_data': 'No location data available for this trip.',
        'location_captured': 'Location is captured when you generate a trip.',
        'delete_confirm': 'Are you sure you want to delete this trip?',
        'delete_success': 'Trip deleted successfully!',
        'delete_error': 'Trip not found or you do not have permission to delete it.',
        'login_required': 'Please login first',
        'fill_all_fields': 'Please fill in all fields',
        'password_mismatch': 'Passwords do not match',
        'password_min': 'Password must be at least 6 characters',
        'email_registered': 'Email already registered. Please login.',
        'welcome_user': 'Welcome to AI Travel Planner',
        'welcome_back_user': 'Welcome back',
        'logged_out': 'You have been logged out',
        'generation_error': 'An error occurred while generating your itinerary. Please try again.',
        'trip_not_found': 'Trip not found or you do not have permission to view it.',
        'invalid_credentials': 'Invalid email or password',
        'register_success': 'Registration successful!',
        'location_detected': '📍 Location detected',
        'detecting_location': 'Getting your location...',
        'location_denied': '⚠️ Location access denied. Using default location.',
        'location_not_supported': '⚠️ Geolocation not supported. Using default location.',
        'home_link': '🏠 Home',
        'destination_letters': 'Destination should only contain letters and spaces',
        'days_number': 'Days must be a valid number',
        'budget_number': 'Budget must be a valid number',
        'travelers_number': 'Travelers must be a valid number',
        'invalid_input': 'Invalid input. Please check your entries.',
    },
    'hi': {
        'welcome': 'स्वागत है',
        'plan_dream': 'AI के साथ अपनी सपनों की यात्रा की योजना बनाएं',
        'discover_destinations': 'गंतव्यों की खोज करें, व्यक्तिगत यात्रा कार्यक्रम बनाएं, बजट का अनुमान लगाएं, और कृत्रिम बुद्धिमत्ता के साथ बेहतर यात्रा करें।',
        'popular_destinations': 'लोकप्रिय गंतव्य',
        'explore_destinations': 'दुनिया भर में सबसे पसंदीदा गंतव्यों का अन्वेषण करें',
        'generate_trip': 'AI यात्रा बनाएं',
        'destination': 'गंतव्य',
        'days': 'दिन',
        'budget': 'बजट (₹)',
        'travelers': 'यात्री',
        'style': 'यात्रा शैली',
        'interests': 'रुचियां (अल्पविराम से अलग करें)',
        'saved_trips': 'मेरी सहेजी गई यात्राएं',
        'login': 'लॉगिन',
        'register': 'रजिस्टर',
        'logout': 'लॉगआउट',
        'dashboard': 'डैशबोर्ड',
        'home': 'होम',
        'no_trips': 'कोई यात्रा नहीं मिली',
        'generate_first': 'अपनी पहली यात्रा बनाएं',
        'welcome_back': 'वापस स्वागत है',
        'language': 'भाषा',
        'my_trips': 'मेरी यात्राएं',
        'total_trips': 'कुल यात्राएं',
        'destinations': 'गंतव्य',
        'total_budget': 'कुल बजट',
        'max_budget': 'अधिकतम बजट (₹)',
        'destination_filter': 'गंतव्य',
        'search_destination': 'गंतव्य खोजें...',
        'sort_by': 'क्रमबद्ध करें',
        'newest': 'नवीनतम',
        'oldest': 'सबसे पुराना',
        'budget_high': 'बजट: उच्च-निम्न',
        'budget_low': 'बजट: निम्न-उच्च',
        'apply_filters': 'फ़िल्टर लागू करें',
        'clear': 'साफ़ करें',
        'days_short': 'दिन',
        'actions': 'कार्य',
        'view': 'देखें',
        'delete': 'हटाएं',
        'no_preview': 'कोई पूर्वावलोकन उपलब्ध नहीं',
        'no_trips_match': 'कोई यात्रा आपके फ़िल्टर से मेल नहीं खाती। कृपया अपने खोज मानदंड समायोजित करें।',
        'no_trips_yet': 'आपने अभी तक कोई यात्रा योजना नहीं बनाई है। अपना साहसिक कार्य अभी शुरू करें!',
        'login_title': 'अपने AI यात्रा योजनाकार खाते में लॉगिन करें',
        'email': 'ईमेल पता',
        'password': 'पासवर्ड',
        'enter_email': 'अपना ईमेल दर्ज करें',
        'enter_password': 'अपना पासवर्ड दर्ज करें',
        'no_account': 'खाता नहीं है?',
        'create_account': 'खाता बनाएं',
        'back_home': '← होम पर वापस जाएं',
        'register_title': 'AI के साथ अपनी सपनों की यात्रा की योजना बनाना शुरू करें',
        'full_name': 'पूरा नाम',
        'enter_name': 'अपना पूरा नाम दर्ज करें',
        'create_password': 'पासवर्ड बनाएं (न्यूनतम 6 अक्षर)',
        'confirm_password': 'पासवर्ड की पुष्टि करें',
        'confirm_password_placeholder': 'अपने पासवर्ड की पुष्टि करें',
        'already_account': 'पहले से खाता है?',
        'weak_password': 'कमजोर पासवर्ड',
        'medium_password': 'मध्यम पासवर्ड',
        'strong_password': 'मजबूत पासवर्ड',
        'trip_plan': 'आपकी यात्रा योजना',
        'destination_label': 'गंतव्य:',
        'your_budget': 'आपका बजट',
        'trip_generated': '✅ आपके निर्दिष्ट बजट के भीतर यात्रा उत्पन्न की गई',
        'view_all_trips': '📋 सभी यात्राएं देखें',
        'plan_another': '✈ एक और यात्रा योजना बनाएं',
        'back_to_dashboard': '← डैशबोर्ड पर वापस जाएं',
        'location_map': '📍 स्थान मानचित्र',
        'open_in_map': '🌍 OpenStreetMap में खोलें',
        'no_location_data': 'इस यात्रा के लिए कोई स्थान डेटा उपलब्ध नहीं है।',
        'location_captured': 'जब आप यात्रा उत्पन्न करते हैं तो स्थान कैप्चर किया जाता है।',
        'delete_confirm': 'क्या आप वाकई इस यात्रा को हटाना चाहते हैं?',
        'delete_success': 'यात्रा सफलतापूर्वक हटा दी गई!',
        'delete_error': 'यात्रा नहीं मिली या आपके पास इसे हटाने की अनुमति नहीं है।',
        'login_required': 'कृपया पहले लॉगिन करें',
        'fill_all_fields': 'कृपया सभी फ़ील्ड भरें',
        'password_mismatch': 'पासवर्ड मेल नहीं खाते',
        'password_min': 'पासवर्ड कम से कम 6 अक्षर का होना चाहिए',
        'email_registered': 'ईमेल पहले से पंजीकृत है। कृपया लॉगिन करें।',
        'welcome_user': 'AI यात्रा योजनाकार में आपका स्वागत है',
        'welcome_back_user': 'वापस स्वागत है',
        'logged_out': 'आप लॉगआउट हो गए हैं',
        'generation_error': 'आपकी यात्रा कार्यक्रम उत्पन्न करते समय एक त्रुटि हुई। कृपया पुनः प्रयास करें।',
        'trip_not_found': 'यात्रा नहीं मिली या आपके पास इसे देखने की अनुमति नहीं है।',
        'invalid_credentials': 'अमान्य ईमेल या पासवर्ड',
        'register_success': 'पंजीकरण सफल!',
        'location_detected': '📍 स्थान का पता चला',
        'detecting_location': 'आपका स्थान प्राप्त किया जा रहा है...',
        'location_denied': '⚠️ स्थान पहुंच अस्वीकृत। डिफ़ॉल्ट स्थान का उपयोग कर रहे हैं।',
        'location_not_supported': '⚠️ जियोलोकेशन समर्थित नहीं है। डिफ़ॉल्ट स्थान का उपयोग कर रहे हैं।',
        'home_link': '🏠 होम',
        'destination_letters': 'गंतव्य में केवल अक्षर और रिक्त स्थान होने चाहिए',
        'days_number': 'दिन एक मान्य संख्या होनी चाहिए',
        'budget_number': 'बजट एक मान्य संख्या होनी चाहिए',
        'travelers_number': 'यात्री एक मान्य संख्या होनी चाहिए',
        'invalid_input': 'अमान्य इनपुट। कृपया अपनी प्रविष्टियाँ जांचें।',
    },
    'ta': {
        'welcome': 'வரவேற்கிறோம்',
        'plan_dream': 'AI உடன் உங்கள் கனவு பயணத்தை திட்டமிடுங்கள்',
        'discover_destinations': 'இலக்குகளைக் கண்டறியவும், தனிப்பயனாக்கப்பட்ட பயணத் திட்டங்களை உருவாக்கவும், பட்ஜெட்டை மதிப்பிடவும், செயற்கை நுண்ணறிவுடன் புத்திசாலித்தனமாக பயணிக்கவும்.',
        'popular_destinations': 'பிரபலமான இலக்குகள்',
        'explore_destinations': 'உலகெங்கிலும் உள்ள மிகவும் விரும்பப்படும் இலக்குகளை ஆராயுங்கள்',
        'generate_trip': 'AI பயணத்தை உருவாக்கு',
        'destination': 'இலக்கு',
        'days': 'நாட்கள்',
        'budget': 'பட்ஜெட் (₹)',
        'travelers': 'பயணிகள்',
        'style': 'பயண பாணி',
        'interests': 'ஆர்வங்கள் (கமாவால் பிரிக்கவும்)',
        'saved_trips': 'எனது சேமித்த பயணங்கள்',
        'login': 'உள்நுழைய',
        'register': 'பதிவு செய்க',
        'logout': 'வெளியேறு',
        'dashboard': 'டாஷ்போர்டு',
        'home': 'முகப்பு',
        'no_trips': 'பயணங்கள் எதுவும் கிடைக்கவில்லை',
        'generate_first': 'உங்கள் முதல் பயணத்தை உருவாக்குங்கள்',
        'welcome_back': 'மீண்டும் வரவேற்கிறோம்',
        'language': 'மொழி',
        'my_trips': 'எனது பயணங்கள்',
        'total_trips': 'மொத்த பயணங்கள்',
        'destinations': 'இலக்குகள்',
        'total_budget': 'மொத்த பட்ஜெட்',
        'max_budget': 'அதிகபட்ச பட்ஜெட் (₹)',
        'destination_filter': 'இலக்கு',
        'search_destination': 'இலக்கைத் தேடுங்கள்...',
        'sort_by': 'வரிசைப்படுத்து',
        'newest': 'புதியவை',
        'oldest': 'பழையவை',
        'budget_high': 'பட்ஜெட்: உயர்-தாழ்',
        'budget_low': 'பட்ஜெட்: தாழ்-உயர்',
        'apply_filters': 'வடிப்பான்களைப் பயன்படுத்து',
        'clear': 'அழிக்கவும்',
        'days_short': 'நாட்கள்',
        'actions': 'செயல்கள்',
        'view': 'பார்க்கவும்',
        'delete': 'நீக்கவும்',
        'no_preview': 'முன்னோட்டம் இல்லை',
        'no_trips_match': 'உங்கள் வடிப்பான்களுடன் பொருந்தக்கூடிய பயணங்கள் இல்லை. உங்கள் தேடல் அளவுகோல்களை மாற்றவும்.',
        'no_trips_yet': 'நீங்கள் இன்னும் எந்த பயணத்தையும் திட்டமிடவில்லை. இப்போது உங்கள் சாகசத்தைத் தொடங்குங்கள்!',
        'login_title': 'உங்கள் AI பயண திட்டமிடுபவர் கணக்கில் உள்நுழையவும்',
        'email': 'மின்னஞ்சல் முகவரி',
        'password': 'கடவுச்சொல்',
        'enter_email': 'உங்கள் மின்னஞ்சலை உள்ளிடவும்',
        'enter_password': 'உங்கள் கடவுச்சொல்லை உள்ளிடவும்',
        'no_account': 'கணக்கு இல்லையா?',
        'create_account': 'கணக்கு உருவாக்கு',
        'back_home': '← முகப்புக்கு திரும்பு',
        'register_title': 'AI உடன் உங்கள் கனவு பயணத்தை திட்டமிடத் தொடங்குங்கள்',
        'full_name': 'முழு பெயர்',
        'enter_name': 'உங்கள் முழு பெயரை உள்ளிடவும்',
        'create_password': 'கடவுச்சொல் உருவாக்கு (குறைந்தது 6 எழுத்துகள்)',
        'confirm_password': 'கடவுச்சொல்லை உறுதிப்படுத்தவும்',
        'confirm_password_placeholder': 'உங்கள் கடவுச்சொல்லை உறுதிப்படுத்தவும்',
        'already_account': 'ஏற்கனவே கணக்கு உள்ளதா?',
        'weak_password': 'பலவீனமான கடவுச்சொல்',
        'medium_password': 'மிதமான கடவுச்சொல்',
        'strong_password': 'வலுவான கடவுச்சொல்',
        'trip_plan': 'உங்கள் பயண திட்டம்',
        'destination_label': 'இலக்கு:',
        'your_budget': 'உங்கள் பட்ஜெட்',
        'trip_generated': '✅ உங்கள் குறிப்பிட்ட பட்ஜெட்டில் பயணம் உருவாக்கப்பட்டது',
        'view_all_trips': '📋 அனைத்து பயணங்களையும் காண்க',
        'plan_another': '✈ இன்னொரு பயணத்தை திட்டமிடு',
        'back_to_dashboard': '← டாஷ்போர்டுக்கு திரும்பு',
        'location_map': '📍 இருப்பிட வரைபடம்',
        'open_in_map': '🌍 OpenStreetMap இல் திறக்கவும்',
        'no_location_data': 'இந்த பயணத்திற்கு இருப்பிட தரவு இல்லை.',
        'location_captured': 'நீங்கள் பயணத்தை உருவாக்கும்போது இருப்பிடம் பிடிக்கப்படும்.',
        'delete_confirm': 'இந்த பயணத்தை நீக்க விரும்புகிறீர்களா?',
        'delete_success': 'பயணம் வெற்றிகரமாக நீக்கப்பட்டது!',
        'delete_error': 'பயணம் கிடைக்கவில்லை அல்லது அதை நீக்க உங்களுக்கு அனுமதி இல்லை.',
        'login_required': 'தயவுசெய்து முதலில் உள்நுழையவும்',
        'fill_all_fields': 'அனைத்து புலங்களையும் நிரப்பவும்',
        'password_mismatch': 'கடவுச்சொற்கள் பொருந்தவில்லை',
        'password_min': 'கடவுச்சொல் குறைந்தது 6 எழுத்துகளாக இருக்க வேண்டும்',
        'email_registered': 'மின்னஞ்சல் ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது. தயவுசெய்து உள்நுழையவும்.',
        'welcome_user': 'AI பயண திட்டமிடுபவருக்கு வரவேற்கிறோம்',
        'welcome_back_user': 'மீண்டும் வரவேற்கிறோம்',
        'logged_out': 'நீங்கள் வெளியேறிவிட்டீர்கள்',
        'generation_error': 'உங்கள் பயணத் திட்டத்தை உருவாக்கும் போது பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.',
        'trip_not_found': 'பயணம் கிடைக்கவில்லை அல்லது அதைப் பார்க்க உங்களுக்கு அனுமதி இல்லை.',
        'invalid_credentials': 'தவறான மின்னஞ்சல் அல்லது கடவுச்சொல்',
        'register_success': 'பதிவு வெற்றிகரமானது!',
        'location_detected': '📍 இருப்பிடம் கண்டறியப்பட்டது',
        'detecting_location': 'உங்கள் இருப்பிடத்தைப் பெறுகிறது...',
        'location_denied': '⚠️ இருப்பிட அணுகல் மறுக்கப்பட்டது. இயல்புநிலை இருப்பிடத்தைப் பயன்படுத்துகிறது.',
        'location_not_supported': '⚠️ புவிஇருப்பிடம் ஆதரிக்கப்படவில்லை. இயல்புநிலை இருப்பிடத்தைப் பயன்படுத்துகிறது.',
        'home_link': '🏠 முகப்பு',
        'destination_letters': 'இலக்கில் எழுத்துக்கள் மற்றும் இடைவெளிகள் மட்டுமே இருக்க வேண்டும்',
        'days_number': 'நாட்கள் ஒரு செல்லுபடியாகும் எண்ணாக இருக்க வேண்டும்',
        'budget_number': 'பட்ஜெட் ஒரு செல்லுபடியாகும் எண்ணாக இருக்க வேண்டும்',
        'travelers_number': 'பயணிகள் ஒரு செல்லுபடியாகும் எண்ணாக இருக்க வேண்டும்',
        'invalid_input': 'தவறான உள்ளீடு. உங்கள் உள்ளீடுகளைச் சரிபார்க்கவும்.',
    },
    'es': {
        'welcome': 'Bienvenido',
        'plan_dream': 'Planifica tu viaje soñado con IA',
        'discover_destinations': 'Descubre destinos, genera itinerarios personalizados, estima presupuestos y viaja de manera más inteligente con Inteligencia Artificial.',
        'popular_destinations': 'Destinos Populares',
        'explore_destinations': 'Explora los destinos más queridos del mundo',
        'generate_trip': 'Generar Viaje con IA',
        'destination': 'Destino',
        'days': 'Días',
        'budget': 'Presupuesto (₹)',
        'travelers': 'Viajeros',
        'style': 'Estilo de Viaje',
        'interests': 'Intereses (separados por comas)',
        'saved_trips': 'Mis Viajes Guardados',
        'login': 'Iniciar Sesión',
        'register': 'Registrarse',
        'logout': 'Cerrar Sesión',
        'dashboard': 'Tablero',
        'home': 'Inicio',
        'no_trips': 'No se encontraron viajes',
        'generate_first': 'Genera tu primer viaje',
        'welcome_back': 'Bienvenido de nuevo',
        'language': 'Idioma',
        'my_trips': 'Mis Viajes',
        'total_trips': 'Total de Viajes',
        'destinations': 'Destinos',
        'total_budget': 'Presupuesto Total',
        'max_budget': 'Presupuesto Máximo (₹)',
        'destination_filter': 'Destino',
        'search_destination': 'Buscar destino...',
        'sort_by': 'Ordenar por',
        'newest': 'Más reciente',
        'oldest': 'Más antiguo',
        'budget_high': 'Presupuesto: Alto-Bajo',
        'budget_low': 'Presupuesto: Bajo-Alto',
        'apply_filters': 'Aplicar Filtros',
        'clear': 'Limpiar',
        'days_short': 'días',
        'actions': 'Acciones',
        'view': 'Ver',
        'delete': 'Eliminar',
        'no_preview': 'No hay vista previa disponible',
        'no_trips_match': 'No hay viajes que coincidan con tus filtros. Ajusta tus criterios de búsqueda.',
        'no_trips_yet': 'Aún no has planificado ningún viaje. ¡Comienza tu aventura ahora!',
        'login_title': 'Inicia sesión en tu cuenta de Planificador de Viajes con IA',
        'email': 'Correo Electrónico',
        'password': 'Contraseña',
        'enter_email': 'Ingresa tu correo electrónico',
        'enter_password': 'Ingresa tu contraseña',
        'no_account': '¿No tienes cuenta?',
        'create_account': 'Crear Cuenta',
        'back_home': '← Volver al Inicio',
        'register_title': 'Comienza a planificar tu viaje soñado con IA',
        'full_name': 'Nombre Completo',
        'enter_name': 'Ingresa tu nombre completo',
        'create_password': 'Crea una contraseña (mínimo 6 caracteres)',
        'confirm_password': 'Confirmar Contraseña',
        'confirm_password_placeholder': 'Confirma tu contraseña',
        'already_account': '¿Ya tienes cuenta?',
        'weak_password': 'Contraseña débil',
        'medium_password': 'Contraseña media',
        'strong_password': 'Contraseña fuerte',
        'trip_plan': 'Tu Plan de Viaje',
        'destination_label': 'Destino:',
        'your_budget': 'Tu Presupuesto',
        'trip_generated': '✅ Viaje generado dentro de tu presupuesto especificado',
        'view_all_trips': '📋 Ver Todos los Viajes',
        'plan_another': '✈ Planificar Otro Viaje',
        'back_to_dashboard': '← Volver al Tablero',
        'location_map': '📍 Mapa de Ubicación',
        'open_in_map': '🌍 Abrir en OpenStreetMap',
        'no_location_data': 'No hay datos de ubicación disponibles para este viaje.',
        'location_captured': 'La ubicación se captura cuando generas un viaje.',
        'delete_confirm': '¿Estás seguro de que quieres eliminar este viaje?',
        'delete_success': '¡Viaje eliminado exitosamente!',
        'delete_error': 'Viaje no encontrado o no tienes permiso para eliminarlo.',
        'login_required': 'Por favor, inicia sesión primero',
        'fill_all_fields': 'Por favor, completa todos los campos',
        'password_mismatch': 'Las contraseñas no coinciden',
        'password_min': 'La contraseña debe tener al menos 6 caracteres',
        'email_registered': 'El correo electrónico ya está registrado. Por favor, inicia sesión.',
        'welcome_user': 'Bienvenido al Planificador de Viajes con IA',
        'welcome_back_user': 'Bienvenido de nuevo',
        'logged_out': 'Has cerrado sesión',
        'generation_error': 'Ocurrió un error al generar tu itinerario. Intenta de nuevo.',
        'trip_not_found': 'Viaje no encontrado o no tienes permiso para verlo.',
        'invalid_credentials': 'Correo electrónico o contraseña inválidos',
        'register_success': '¡Registro exitoso!',
        'location_detected': '📍 Ubicación detectada',
        'detecting_location': 'Obteniendo tu ubicación...',
        'location_denied': '⚠️ Acceso a ubicación denegado. Usando ubicación predeterminada.',
        'location_not_supported': '⚠️ Geolocalización no soportada. Usando ubicación predeterminada.',
        'home_link': '🏠 Inicio',
        'destination_letters': 'El destino solo debe contener letras y espacios',
        'days_number': 'Los días deben ser un número válido',
        'budget_number': 'El presupuesto debe ser un número válido',
        'travelers_number': 'Los viajeros deben ser un número válido',
        'invalid_input': 'Entrada inválida. Por favor revisa tus entradas.',
    },
    'fr': {
        'welcome': 'Bienvenue',
        'plan_dream': 'Planifiez votre voyage de rêve avec l\'IA',
        'discover_destinations': 'Découvrez des destinations, générez des itinéraires personnalisés, estimez les budgets et voyagez plus intelligemment avec l\'intelligence artificielle.',
        'popular_destinations': 'Destinations Populaires',
        'explore_destinations': 'Explorez les destinations les plus appréciées du monde',
        'generate_trip': 'Générer un Voyage IA',
        'destination': 'Destination',
        'days': 'Jours',
        'budget': 'Budget (₹)',
        'travelers': 'Voyageurs',
        'style': 'Style de Voyage',
        'interests': 'Centres d\'intérêt (séparés par des virgules)',
        'saved_trips': 'Mes Voyages Sauvegardés',
        'login': 'Se Connecter',
        'register': 'S\'inscrire',
        'logout': 'Se Déconnecter',
        'dashboard': 'Tableau de Bord',
        'home': 'Accueil',
        'no_trips': 'Aucun voyage trouvé',
        'generate_first': 'Générez votre premier voyage',
        'welcome_back': 'Bon retour',
        'language': 'Langue',
        'my_trips': 'Mes Voyages',
        'total_trips': 'Total des Voyages',
        'destinations': 'Destinations',
        'total_budget': 'Budget Total',
        'max_budget': 'Budget Maximum (₹)',
        'destination_filter': 'Destination',
        'search_destination': 'Rechercher une destination...',
        'sort_by': 'Trier par',
        'newest': 'Plus récent',
        'oldest': 'Plus ancien',
        'budget_high': 'Budget: Élevé-Bas',
        'budget_low': 'Budget: Bas-Élevé',
        'apply_filters': 'Appliquer les Filtres',
        'clear': 'Effacer',
        'days_short': 'jours',
        'actions': 'Actions',
        'view': 'Voir',
        'delete': 'Supprimer',
        'no_preview': 'Aucun aperçu disponible',
        'no_trips_match': 'Aucun voyage ne correspond à vos filtres. Ajustez vos critères de recherche.',
        'no_trips_yet': 'Vous n\'avez pas encore planifié de voyage. Commencez votre aventure maintenant !',
        'login_title': 'Connectez-vous à votre compte Planificateur de Voyage IA',
        'email': 'Adresse Email',
        'password': 'Mot de Passe',
        'enter_email': 'Entrez votre email',
        'enter_password': 'Entrez votre mot de passe',
        'no_account': 'Vous n\'avez pas de compte ?',
        'create_account': 'Créer un Compte',
        'back_home': '← Retour à l\'Accueil',
        'register_title': 'Commencez à planifier votre voyage de rêve avec l\'IA',
        'full_name': 'Nom Complet',
        'enter_name': 'Entrez votre nom complet',
        'create_password': 'Créez un mot de passe (minimum 6 caractères)',
        'confirm_password': 'Confirmer le Mot de Passe',
        'confirm_password_placeholder': 'Confirmez votre mot de passe',
        'already_account': 'Vous avez déjà un compte ?',
        'weak_password': 'Mot de passe faible',
        'medium_password': 'Mot de passe moyen',
        'strong_password': 'Mot de passe fort',
        'trip_plan': 'Votre Plan de Voyage',
        'destination_label': 'Destination :',
        'your_budget': 'Votre Budget',
        'trip_generated': '✅ Voyage généré dans votre budget spécifié',
        'view_all_trips': '📋 Voir Tous les Voyages',
        'plan_another': '✈ Planifier un Autre Voyage',
        'back_to_dashboard': '← Retour au Tableau de Bord',
        'location_map': '📍 Carte de Localisation',
        'open_in_map': '🌍 Ouvrir dans OpenStreetMap',
        'no_location_data': 'Aucune donnée de localisation disponible pour ce voyage.',
        'location_captured': 'La localisation est capturée lorsque vous générez un voyage.',
        'delete_confirm': 'Êtes-vous sûr de vouloir supprimer ce voyage ?',
        'delete_success': 'Voyage supprimé avec succès !',
        'delete_error': 'Voyage non trouvé ou vous n\'avez pas la permission de le supprimer.',
        'login_required': 'Veuillez vous connecter d\'abord',
        'fill_all_fields': 'Veuillez remplir tous les champs',
        'password_mismatch': 'Les mots de passe ne correspondent pas',
        'password_min': 'Le mot de passe doit contenir au moins 6 caractères',
        'email_registered': 'L\'email est déjà enregistré. Veuillez vous connecter.',
        'welcome_user': 'Bienvenue dans le Planificateur de Voyage IA',
        'welcome_back_user': 'Bon retour',
        'logged_out': 'Vous vous êtes déconnecté',
        'generation_error': 'Une erreur est survenue lors de la génération de votre itinéraire. Veuillez réessayer.',
        'trip_not_found': 'Voyage non trouvé ou vous n\'avez pas la permission de le voir.',
        'invalid_credentials': 'Email ou mot de passe invalide',
        'register_success': 'Inscription réussie !',
        'location_detected': '📍 Localisation détectée',
        'detecting_location': 'Obtention de votre localisation...',
        'location_denied': '⚠️ Accès à la localisation refusé. Utilisation de la localisation par défaut.',
        'location_not_supported': '⚠️ Géolocalisation non prise en charge. Utilisation de la localisation par défaut.',
        'home_link': '🏠 Accueil',
        'destination_letters': 'La destination ne doit contenir que des lettres et des espaces',
        'days_number': 'Les jours doivent être un nombre valide',
        'budget_number': 'Le budget doit être un nombre valide',
        'travelers_number': 'Les voyageurs doivent être un nombre valide',
        'invalid_input': 'Entrée invalide. Veuillez vérifier vos entrées.',
    },
    'de': {
        'welcome': 'Willkommen',
        'plan_dream': 'Planen Sie Ihre Traumreise mit KI',
        'discover_destinations': 'Entdecken Sie Reiseziele, generieren Sie personalisierte Reisepläne, schätzen Sie Budgets und reisen Sie intelligenter mit Künstlicher Intelligenz.',
        'popular_destinations': 'Beliebte Reiseziele',
        'explore_destinations': 'Entdecken Sie die beliebtesten Reiseziele der Welt',
        'generate_trip': 'KI-Reise generieren',
        'destination': 'Reiseziel',
        'days': 'Tage',
        'budget': 'Budget (₹)',
        'travelers': 'Reisende',
        'style': 'Reisestil',
        'interests': 'Interessen (kommagetrennt)',
        'saved_trips': 'Meine gespeicherten Reisen',
        'login': 'Anmelden',
        'register': 'Registrieren',
        'logout': 'Abmelden',
        'dashboard': 'Dashboard',
        'home': 'Startseite',
        'no_trips': 'Keine Reisen gefunden',
        'generate_first': 'Generieren Sie Ihre erste Reise',
        'welcome_back': 'Willkommen zurück',
        'language': 'Sprache',
        'my_trips': 'Meine Reisen',
        'total_trips': 'Gesamtzahl der Reisen',
        'destinations': 'Reiseziele',
        'total_budget': 'Gesamtbudget',
        'max_budget': 'Maximales Budget (₹)',
        'destination_filter': 'Reiseziel',
        'search_destination': 'Reiseziel suchen...',
        'sort_by': 'Sortieren nach',
        'newest': 'Neueste',
        'oldest': 'Älteste',
        'budget_high': 'Budget: Hoch-Niedrig',
        'budget_low': 'Budget: Niedrig-Hoch',
        'apply_filters': 'Filter anwenden',
        'clear': 'Löschen',
        'days_short': 'Tage',
        'actions': 'Aktionen',
        'view': 'Ansehen',
        'delete': 'Löschen',
        'no_preview': 'Keine Vorschau verfügbar',
        'no_trips_match': 'Keine Reisen entsprechen Ihren Filtern. Passen Sie Ihre Suchkriterien an.',
        'no_trips_yet': 'Sie haben noch keine Reisen geplant. Starten Sie jetzt Ihr Abenteuer!',
        'login_title': 'Melden Sie sich bei Ihrem KI-Reiseplaner-Konto an',
        'email': 'E-Mail-Adresse',
        'password': 'Passwort',
        'enter_email': 'Geben Sie Ihre E-Mail ein',
        'enter_password': 'Geben Sie Ihr Passwort ein',
        'no_account': 'Sie haben kein Konto?',
        'create_account': 'Konto erstellen',
        'back_home': '← Zurück zur Startseite',
        'register_title': 'Beginnen Sie mit der Planung Ihrer Traumreise mit KI',
        'full_name': 'Vollständiger Name',
        'enter_name': 'Geben Sie Ihren vollständigen Namen ein',
        'create_password': 'Erstellen Sie ein Passwort (mindestens 6 Zeichen)',
        'confirm_password': 'Passwort bestätigen',
        'confirm_password_placeholder': 'Bestätigen Sie Ihr Passwort',
        'already_account': 'Sie haben bereits ein Konto?',
        'weak_password': 'Schwaches Passwort',
        'medium_password': 'Mittleres Passwort',
        'strong_password': 'Starkes Passwort',
        'trip_plan': 'Ihr Reiseplan',
        'destination_label': 'Reiseziel:',
        'your_budget': 'Ihr Budget',
        'trip_generated': '✅ Reise innerhalb Ihres angegebenen Budgets generiert',
        'view_all_trips': '📋 Alle Reisen anzeigen',
        'plan_another': '✈ Eine weitere Reise planen',
        'back_to_dashboard': '← Zurück zum Dashboard',
        'location_map': '📍 Standortkarte',
        'open_in_map': '🌍 In OpenStreetMap öffnen',
        'no_location_data': 'Keine Standortdaten für diese Reise verfügbar.',
        'location_captured': 'Der Standort wird erfasst, wenn Sie eine Reise generieren.',
        'delete_confirm': 'Sind Sie sicher, dass Sie diese Reise löschen möchten?',
        'delete_success': 'Reise erfolgreich gelöscht!',
        'delete_error': 'Reise nicht gefunden oder Sie haben keine Berechtigung zum Löschen.',
        'login_required': 'Bitte melden Sie sich zuerst an',
        'fill_all_fields': 'Bitte füllen Sie alle Felder aus',
        'password_mismatch': 'Die Passwörter stimmen nicht überein',
        'password_min': 'Das Passwort muss mindestens 6 Zeichen lang sein',
        'email_registered': 'E-Mail bereits registriert. Bitte melden Sie sich an.',
        'welcome_user': 'Willkommen beim KI-Reiseplaner',
        'welcome_back_user': 'Willkommen zurück',
        'logged_out': 'Sie wurden abgemeldet',
        'generation_error': 'Beim Generieren Ihres Reiseplans ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.',
        'trip_not_found': 'Reise nicht gefunden oder Sie haben keine Berechtigung, sie anzusehen.',
        'invalid_credentials': 'Ungültige E-Mail oder Passwort',
        'register_success': 'Registrierung erfolgreich!',
        'location_detected': '📍 Standort erkannt',
        'detecting_location': 'Ihren Standort wird abgerufen...',
        'location_denied': '⚠️ Standortzugriff verweigert. Verwende Standardstandort.',
        'location_not_supported': '⚠️ Geolokalisierung nicht unterstützt. Verwende Standardstandort.',
        'home_link': '🏠 Startseite',
        'destination_letters': 'Das Reiseziel darf nur Buchstaben und Leerzeichen enthalten',
        'days_number': 'Die Tage müssen eine gültige Zahl sein',
        'budget_number': 'Das Budget muss eine gültige Zahl sein',
        'travelers_number': 'Die Reisenden müssen eine gültige Zahl sein',
        'invalid_input': 'Ungültige Eingabe. Bitte überprüfen Sie Ihre Eingaben.',
    },
    'ja': {
        'welcome': 'ようこそ',
        'plan_dream': 'AIで夢の旅を計画',
        'discover_destinations': '目的地を発見し、パーソナライズされた旅程を生成し、予算を見積もり、人工知能を使ってよりスマートに旅行しましょう。',
        'popular_destinations': '人気の目的地',
        'explore_destinations': '世界中で最も愛されている目的地を探索',
        'generate_trip': 'AI旅行を生成',
        'destination': '目的地',
        'days': '日数',
        'budget': '予算 (₹)',
        'travelers': '旅行者',
        'style': '旅行スタイル',
        'interests': '興味（カンマ区切り）',
        'saved_trips': '保存した旅行',
        'login': 'ログイン',
        'register': '登録',
        'logout': 'ログアウト',
        'dashboard': 'ダッシュボード',
        'home': 'ホーム',
        'no_trips': '旅行が見つかりません',
        'generate_first': '最初の旅行を生成',
        'welcome_back': 'おかえりなさい',
        'language': '言語',
        'my_trips': '私の旅行',
        'total_trips': '総旅行数',
        'destinations': '目的地',
        'total_budget': '総予算',
        'max_budget': '最大予算 (₹)',
        'destination_filter': '目的地',
        'search_destination': '目的地を検索...',
        'sort_by': '並べ替え',
        'newest': '最新',
        'oldest': '最古',
        'budget_high': '予算: 高-低',
        'budget_low': '予算: 低-高',
        'apply_filters': 'フィルターを適用',
        'clear': 'クリア',
        'days_short': '日',
        'actions': 'アクション',
        'view': '表示',
        'delete': '削除',
        'no_preview': 'プレビューはありません',
        'no_trips_match': 'フィルターに一致する旅行はありません。検索条件を調整してください。',
        'no_trips_yet': 'まだ旅行を計画していません。今すぐ冒険を始めましょう！',
        'login_title': 'AI旅行プランナーアカウントにログイン',
        'email': 'メールアドレス',
        'password': 'パスワード',
        'enter_email': 'メールアドレスを入力',
        'enter_password': 'パスワードを入力',
        'no_account': 'アカウントをお持ちでない方',
        'create_account': 'アカウント作成',
        'back_home': '← ホームに戻る',
        'register_title': 'AIで夢の旅の計画を始めましょう',
        'full_name': 'フルネーム',
        'enter_name': 'フルネームを入力',
        'create_password': 'パスワードを作成（6文字以上）',
        'confirm_password': 'パスワード確認',
        'confirm_password_placeholder': 'パスワードを確認',
        'already_account': 'すでにアカウントをお持ちの方',
        'weak_password': '弱いパスワード',
        'medium_password': '中程度のパスワード',
        'strong_password': '強いパスワード',
        'trip_plan': '旅行プラン',
        'destination_label': '目的地:',
        'your_budget': 'あなたの予算',
        'trip_generated': '✅ 指定された予算内で旅行が生成されました',
        'view_all_trips': '📋 すべての旅行を表示',
        'plan_another': '✈ 別の旅行を計画',
        'back_to_dashboard': '← ダッシュボードに戻る',
        'location_map': '📍 位置マップ',
        'open_in_map': '🌍 OpenStreetMapで開く',
        'no_location_data': 'この旅行の位置データはありません。',
        'location_captured': '旅行を生成するときに位置情報が取得されます。',
        'delete_confirm': 'この旅行を削除してもよろしいですか？',
        'delete_success': '旅行が正常に削除されました！',
        'delete_error': '旅行が見つからないか、削除する権限がありません。',
        'login_required': 'まずログインしてください',
        'fill_all_fields': 'すべてのフィールドに入力してください',
        'password_mismatch': 'パスワードが一致しません',
        'password_min': 'パスワードは6文字以上必要です',
        'email_registered': 'メールアドレスは既に登録されています。ログインしてください。',
        'welcome_user': 'AI旅行プランナーへようこそ',
        'welcome_back_user': 'おかえりなさい',
        'logged_out': 'ログアウトしました',
        'generation_error': '旅程の生成中にエラーが発生しました。もう一度お試しください。',
        'trip_not_found': '旅行が見つからないか、表示する権限がありません。',
        'invalid_credentials': '無効なメールアドレスまたはパスワード',
        'register_success': '登録が成功しました！',
        'location_detected': '📍 位置を検出しました',
        'detecting_location': '位置情報を取得中...',
        'location_denied': '⚠️ 位置情報へのアクセスが拒否されました。デフォルトの位置を使用します。',
        'location_not_supported': '⚠️ 位置情報がサポートされていません。デフォルトの位置を使用します。',
        'home_link': '🏠 ホーム',
        'destination_letters': '目的地には文字とスペースのみを含める必要があります',
        'days_number': '日数は有効な数字である必要があります',
        'budget_number': '予算は有効な数字である必要があります',
        'travelers_number': '旅行者は有効な数字である必要があります',
        'invalid_input': '無効な入力です。入力を確認してください。',
    },
    'zh': {
        'welcome': '欢迎',
        'plan_dream': '使用AI规划您的梦想之旅',
        'discover_destinations': '发现目的地，生成个性化行程，估算预算，并利用人工智能更智能地旅行。',
        'popular_destinations': '热门目的地',
        'explore_destinations': '探索全球最受欢迎的目的地',
        'generate_trip': '生成AI旅行',
        'destination': '目的地',
        'days': '天数',
        'budget': '预算 (₹)',
        'travelers': '旅行者',
        'style': '旅行风格',
        'interests': '兴趣（用逗号分隔）',
        'saved_trips': '我保存的旅行',
        'login': '登录',
        'register': '注册',
        'logout': '登出',
        'dashboard': '仪表板',
        'home': '首页',
        'no_trips': '未找到旅行',
        'generate_first': '生成您的第一次旅行',
        'welcome_back': '欢迎回来',
        'language': '语言',
        'my_trips': '我的旅行',
        'total_trips': '旅行总数',
        'destinations': '目的地',
        'total_budget': '总预算',
        'max_budget': '最大预算 (₹)',
        'destination_filter': '目的地',
        'search_destination': '搜索目的地...',
        'sort_by': '排序方式',
        'newest': '最新',
        'oldest': '最旧',
        'budget_high': '预算: 高-低',
        'budget_low': '预算: 低-高',
        'apply_filters': '应用筛选',
        'clear': '清除',
        'days_short': '天',
        'actions': '操作',
        'view': '查看',
        'delete': '删除',
        'no_preview': '没有预览',
        'no_trips_match': '没有旅行符合您的筛选条件。请调整搜索条件。',
        'no_trips_yet': '您还没有规划任何旅行。现在开始您的冒险！',
        'login_title': '登录您的AI旅行规划器账户',
        'email': '电子邮件',
        'password': '密码',
        'enter_email': '输入您的电子邮件',
        'enter_password': '输入您的密码',
        'no_account': '没有账户？',
        'create_account': '创建账户',
        'back_home': '← 返回首页',
        'register_title': '开始使用AI规划您的梦想之旅',
        'full_name': '全名',
        'enter_name': '输入您的全名',
        'create_password': '创建密码（至少6个字符）',
        'confirm_password': '确认密码',
        'confirm_password_placeholder': '确认您的密码',
        'already_account': '已有账户？',
        'weak_password': '弱密码',
        'medium_password': '中等密码',
        'strong_password': '强密码',
        'trip_plan': '您的旅行计划',
        'destination_label': '目的地:',
        'your_budget': '您的预算',
        'trip_generated': '✅ 在您指定的预算内生成旅行',
        'view_all_trips': '📋 查看所有旅行',
        'plan_another': '✈ 规划另一次旅行',
        'back_to_dashboard': '← 返回仪表板',
        'location_map': '📍 位置地图',
        'open_in_map': '🌍 在OpenStreetMap中打开',
        'no_location_data': '此旅行没有位置数据。',
        'location_captured': '生成旅行时会捕获位置信息。',
        'delete_confirm': '您确定要删除此旅行吗？',
        'delete_success': '旅行已成功删除！',
        'delete_error': '未找到旅行或您没有权限删除它。',
        'login_required': '请先登录',
        'fill_all_fields': '请填写所有字段',
        'password_mismatch': '密码不匹配',
        'password_min': '密码至少需要6个字符',
        'email_registered': '电子邮件已注册。请登录。',
        'welcome_user': '欢迎使用AI旅行规划器',
        'welcome_back_user': '欢迎回来',
        'logged_out': '您已登出',
        'generation_error': '生成行程时出错。请重试。',
        'trip_not_found': '未找到旅行或您没有权限查看它。',
        'invalid_credentials': '无效的电子邮件或密码',
        'register_success': '注册成功！',
        'location_detected': '📍 检测到位置',
        'detecting_location': '正在获取您的位置...',
        'location_denied': '⚠️ 位置访问被拒绝。使用默认位置。',
        'location_not_supported': '⚠️ 不支持地理定位。使用默认位置。',
        'home_link': '🏠 首页',
        'destination_letters': '目的地应仅包含字母和空格',
        'days_number': '天数必须是一个有效的数字',
        'budget_number': '预算必须是一个有效的数字',
        'travelers_number': '旅行者必须是一个有效的数字',
        'invalid_input': '无效输入。请检查您的输入。',
    }
}

def get_translation(lang='en'):
    if lang in TRANSLATIONS:
        return TRANSLATIONS[lang]
    return TRANSLATIONS['en']

@app.context_processor
def context_processor():
    lang = session.get('language', 'en')
    return {
        't': get_translation(lang),
        'lang': lang,
        'languages': LANGUAGES
    }

# ---------------- DATABASE SETUP ----------------

def init_db():
    """Initialize database tables if they don't exist"""
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create trips table with all columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        destination TEXT NOT NULL,
        days TEXT NOT NULL,
        budget TEXT NOT NULL,
        travelers TEXT NOT NULL,
        style TEXT NOT NULL,
        interests TEXT,
        itinerary TEXT,
        latitude REAL,
        longitude REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Add any missing columns
    cursor.execute("PRAGMA table_info(trips)")
    existing = [col[1] for col in cursor.fetchall()]
    
    for col in ['user_id', 'latitude', 'longitude', 'created_at']:
        if col not in existing:
            try:
                if col == 'user_id':
                    cursor.execute("ALTER TABLE trips ADD COLUMN user_id INTEGER")
                elif col == 'created_at':
                    cursor.execute("ALTER TABLE trips ADD COLUMN created_at TIMESTAMP")
                else:
                    cursor.execute(f"ALTER TABLE trips ADD COLUMN {col} REAL")
                print(f"Added {col} column")
            except Exception as e:
                print(f"Could not add {col}: {e}")
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# ---------------- VALIDATION FUNCTIONS ----------------

def validate_destination(dest):
    """Only allow letters, spaces, and basic punctuation"""
    return bool(re.match(r'^[a-zA-Z\s\-.,]+$', dest))

def validate_positive_number(value):
    """Check if value is a positive number"""
    try:
        num = int(value)
        return num > 0
    except ValueError:
        return False

# ---------------- ROUTES ---------------- (rest of the routes remain the same)

@app.route("/")
def root():
    return redirect(url_for("register_page"))

@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in LANGUAGES:
        session['language'] = lang
    else:
        session['language'] = 'en'
    return redirect(request.referrer or url_for('home'))

@app.route("/home")
def home():
    if 'user_id' not in session:
        flash(get_translation(session.get('language', 'en')).get('login_required', 'Please login first'), 'error')
        return redirect(url_for("login_page"))
    return render_template("index.html")

@app.route("/register", methods=["GET"])
def register_page():
    if 'user_id' in session:
        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    lang = session.get('language', 'en')
    t = get_translation(lang)
    
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name or not email or not password:
        flash(t.get('fill_all_fields', 'Please fill in all fields'), 'error')
        return render_template("register.html")

    if password != confirm_password:
        flash(t.get('password_mismatch', 'Passwords do not match'), 'error')
        return render_template("register.html")

    if len(password) < 6:
        flash(t.get('password_min', 'Password must be at least 6 characters'), 'error')
        return render_template("register.html")

    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            flash(t.get('email_registered', 'Email already registered. Please login.'), 'error')
            return render_template("register.html")

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        session['user_id'] = user_id
        session['user_name'] = name
        
        flash(f"{t.get('welcome_user', 'Welcome to AI Travel Planner')}, {name}!", 'success')
        return redirect(url_for("home"))

    except Exception as e:
        conn.close()
        flash(t.get('generation_error', 'An error occurred. Please try again.'), 'error')
        return render_template("register.html")
    finally:
        if conn:
            conn.close()

@app.route("/login", methods=["GET"])
def login_page():
    if 'user_id' in session:
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    lang = session.get('language', 'en')
    t = get_translation(lang)
    
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        flash(t.get('fill_all_fields', 'Please fill in all fields'), 'error')
        return render_template("login.html")

    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        flash(f"{t.get('welcome_back_user', 'Welcome back')}, {user[1]}!", 'success')
        return redirect(url_for("home"))
    else:
        flash(t.get('invalid_credentials', 'Invalid email or password'), 'error')
        return render_template("login.html")

@app.route("/logout")
def logout():
    lang = session.get('language', 'en')
    t = get_translation(lang)
    session.clear()
    flash(t.get('logged_out', 'You have been logged out'), 'success')
    return redirect(url_for("register_page"))

@app.route("/generate", methods=["POST"])
def generate():
    """Generate AI itinerary with budget constraints and input validation"""
    lang = session.get('language', 'en')
    t = get_translation(lang)
    
    if 'user_id' not in session:
        flash(t.get('login_required', 'Please login first'), 'error')
        return redirect(url_for("login_page"))

    destination = request.form.get("destination", "").strip()
    days = request.form.get("days", "").strip()
    budget = request.form.get("budget", "").strip()
    travelers = request.form.get("travelers", "").strip()
    style = request.form.get("style", "")
    interests = request.form.get("interests", "").strip()
    latitude = request.form.get("latitude", "")
    longitude = request.form.get("longitude", "")

    # Validate inputs
    if not destination or not days or not budget or not travelers:
        flash(t.get('fill_all_fields', 'Please fill in all fields'), 'error')
        return redirect(url_for("home"))
    
    # Validate destination - only letters and spaces
    if not validate_destination(destination):
        flash(t.get('destination_letters', 'Destination should only contain letters and spaces'), 'error')
        return redirect(url_for("home"))
    
    # Validate days - positive number
    if not validate_positive_number(days):
        flash(t.get('days_number', 'Days must be a valid number'), 'error')
        return redirect(url_for("home"))
    
    # Validate budget - positive number
    if not validate_positive_number(budget):
        flash(t.get('budget_number', 'Budget must be a valid number'), 'error')
        return redirect(url_for("home"))
    
    # Validate travelers - positive number
    if not validate_positive_number(travelers):
        flash(t.get('travelers_number', 'Travelers must be a valid number'), 'error')
        return redirect(url_for("home"))

    try:
        # Generate AI itinerary with budget constraint
        itinerary = generate_itinerary(
            destination,
            days,
            budget,
            travelers,
            style,
            interests
        )

        # Save trip to database
        conn = sqlite3.connect("travel.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO trips
        (user_id, destination, days, budget, travelers, style, interests, itinerary, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session['user_id'],
            destination,
            days,
            budget,
            travelers,
            style,
            interests,
            itinerary,
            float(latitude) if latitude else None,
            float(longitude) if longitude else None
        ))

        conn.commit()
        conn.close()

        # Convert markdown to HTML
        html = markdown.markdown(itinerary)

        return render_template(
            "result.html",
            destination=destination,
            itinerary=html,
            budget=budget,
            days=days,
            travelers=travelers,
            style=style,
            interests=interests
        )

    except Exception as e:
        print(f"Error: {e}")
        flash(t.get('generation_error', 'An error occurred while generating your itinerary. Please try again.'), 'error')
        return redirect(url_for("home"))

@app.route("/view_trip/<int:trip_id>")
def view_trip(trip_id):
    lang = session.get('language', 'en')
    t = get_translation(lang)
    
    if 'user_id' not in session:
        flash(t.get('login_required', 'Please login first'), 'error')
        return redirect(url_for("login_page"))

    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, destination, days, budget, travelers, style, interests, itinerary, created_at, latitude, longitude
    FROM trips
    WHERE id = ? AND user_id = ?
    """, (trip_id, session['user_id']))

    trip = cursor.fetchone()
    conn.close()

    if not trip:
        flash(t.get('trip_not_found', 'Trip not found or you do not have permission to view it.'), 'error')
        return redirect(url_for("dashboard"))

    html_itinerary = markdown.markdown(trip[7]) if trip[7] else "No itinerary details available."

    return render_template(
        "view_trip.html",
        trip=trip,
        itinerary=html_itinerary,
        has_created_at=True,
        has_coordinates=True
    )

@app.route("/delete_trip/<int:trip_id>", methods=["POST"])
def delete_trip(trip_id):
    lang = session.get('language', 'en')
    t = get_translation(lang)
    
    if 'user_id' not in session:
        flash(t.get('login_required', 'Please login first'), 'error')
        return redirect(url_for("login_page"))

    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM trips WHERE id = ? AND user_id = ?", (trip_id, session['user_id']))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    if rows_affected > 0:
        flash(t.get('delete_success', 'Trip deleted successfully!'), 'success')
    else:
        flash(t.get('delete_error', 'Trip not found or you do not have permission to delete it.'), 'error')

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    lang = session.get('language', 'en')
    t = get_translation(lang)
    
    if 'user_id' not in session:
        flash(t.get('login_required', 'Please login first'), 'error')
        return redirect(url_for("login_page"))

    budget_filter = request.args.get('budget', '').strip()
    destination_filter = request.args.get('destination', '').strip()
    sort_by = request.args.get('sort', 'newest')

    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()

    query = """
    SELECT id, destination, days, budget, travelers, style, interests, 
           itinerary, created_at
    FROM trips
    WHERE user_id = ?
    """
    params = [session['user_id']]

    if budget_filter and budget_filter.isdigit():
        budget_val = int(budget_filter)
        query += " AND CAST(budget AS INTEGER) <= ?"
        params.append(budget_val)

    if destination_filter:
        query += " AND LOWER(destination) LIKE LOWER(?)"
        params.append(f"%{destination_filter}%")

    if sort_by == 'oldest':
        query += " ORDER BY created_at ASC"
    elif sort_by == 'budget_high':
        query += " ORDER BY CAST(budget AS INTEGER) DESC"
    elif sort_by == 'budget_low':
        query += " ORDER BY CAST(budget AS INTEGER) ASC"
    else:
        query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    trips = cursor.fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        trips=trips,
        has_created_at=True
    )
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)