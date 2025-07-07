#!/usr/bin/env python3
"""
Populate known_words table with custom French words
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add src to path
sys.path.append("src")

load_dotenv()

# Use service role key for admin operations
from supabase import create_client, Client

# Create client with service role key (bypasses RLS)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
    print("   Get it from: Supabase Dashboard > Settings > API > service_role key")
    sys.exit(1)

supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def populate_custom_words(user_id: str):
    """Populate with the specific French words list"""
    
    # Custom words with translations and examples using known vocabulary
    custom_words = [
        {
            "user_id": user_id,
            "word": "billet d'avion",
            "translation": "plane ticket",
            "example": "J'ai un billet d'avion pour Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "jardin",
            "translation": "garden",
            "example": "Le chat est dans le jardin.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "appartement",
            "translation": "apartment",
            "example": "J'habite dans un appartement à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "maison",
            "translation": "house",
            "example": "Ma famille habite dans une maison.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "dans",
            "translation": "in",
            "example": "Le chat est dans le jardin.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "veut",
            "translation": "wants",
            "example": "Mon frère veut un animal de compagnie.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "grand-mère",
            "translation": "grandmother",
            "example": "Ma grand-mère habite en France.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "grand-père",
            "translation": "grandfather",
            "example": "Mon grand-père parle français.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "chouette",
            "translation": "owl",
            "example": "Le chouette est un animal de compagnie.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "animal de compagnie",
            "translation": "pet",
            "example": "J'ai un animal de compagnie.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "mari",
            "translation": "husband",
            "example": "Mon mari travaille à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "fils",
            "translation": "son",
            "example": "Mon fils étudie à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "de",
            "translation": "of/from",
            "example": "Je suis de France.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "ma",
            "translation": "my (feminine)",
            "example": "Ma sœur habite à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "sœur",
            "translation": "sister",
            "example": "Ma sœur étudie à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "mère",
            "translation": "mother",
            "example": "Ma mère parle français.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "sa",
            "translation": "his/her (feminine)",
            "example": "Sa famille habite en Espagne.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "famille",
            "translation": "family",
            "example": "Ma famille habite à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "ta",
            "translation": "your (feminine)",
            "example": "Ta sœur habite où?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "son",
            "translation": "his/her (masculine)",
            "example": "Son frère travaille à l'hôtel.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "mon",
            "translation": "my (masculine)",
            "example": "Mon frère habite à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "frère",
            "translation": "brother",
            "example": "Mon frère étudie à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "père",
            "translation": "father",
            "example": "Mon père travaille à l'aéroport.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "ton",
            "translation": "your (masculine)",
            "example": "Ton frère habite où?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "as",
            "translation": "have (you)",
            "example": "Tu as un billet d'avion?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "passeport",
            "translation": "passport",
            "example": "J'ai mon passeport dans ma valise.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "billet",
            "translation": "ticket",
            "example": "J'ai un billet pour le train.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "j'ai",
            "translation": "I have",
            "example": "J'ai un animal de compagnie.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "a",
            "translation": "has",
            "example": "Il a un chat.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "taxi",
            "translation": "taxi",
            "example": "Je prends un taxi pour aller à l'aéroport.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "où",
            "translation": "where",
            "example": "Où habites-tu?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "s'il vous plaît",
            "translation": "please",
            "example": "S'il vous plaît, où est l'hôtel?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "valise",
            "translation": "suitcase",
            "example": "Ma valise est dans le taxi.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "prends",
            "translation": "take",
            "example": "Je prends le train pour aller à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "voiture",
            "translation": "car",
            "example": "Ma voiture est à l'aéroport.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "va",
            "translation": "goes",
            "example": "Il va à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "train",
            "translation": "train",
            "example": "Je prends le train pour aller à la gare.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "hôtel",
            "translation": "hotel",
            "example": "L'hôtel est près de l'aéroport.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "aéroport",
            "translation": "airport",
            "example": "L'aéroport est très grand.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "vas",
            "translation": "go (you)",
            "example": "Tu vas où?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "avion",
            "translation": "plane",
            "example": "L'avion va à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "l'",
            "translation": "the (before vowel)",
            "example": "L'avion est à l'aéroport.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "restaurant",
            "translation": "restaurant",
            "example": "Le restaurant est près de l'hôtel.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "le",
            "translation": "the (masculine)",
            "example": "Le train va à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "vais",
            "translation": "go (I)",
            "example": "Je vais à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "la",
            "translation": "the (feminine)",
            "example": "La gare est près de l'hôtel.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "gare",
            "translation": "train station",
            "example": "La gare est très grande.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "université",
            "translation": "university",
            "example": "L'université est à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "professeur",
            "translation": "professor",
            "example": "Le professeur parle français.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "Italie",
            "translation": "Italy",
            "example": "Je vais en Italie.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "journaliste",
            "translation": "journalist",
            "example": "Le journaliste travaille à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "on",
            "translation": "we/one",
            "example": "On va au restaurant.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "étudies",
            "translation": "study (you)",
            "example": "Tu étudies à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "non",
            "translation": "no",
            "example": "Non, je ne parle pas anglais.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "Espagne",
            "translation": "Spain",
            "example": "Je vais en Espagne.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "Angleterre",
            "translation": "England",
            "example": "Je vais en Angleterre.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "en",
            "translation": "in/to",
            "example": "J'habite en France.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "avec",
            "translation": "with",
            "example": "Je vais au restaurant avec ma famille.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "étudiant",
            "translation": "student (male)",
            "example": "L'étudiant parle français.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "ici",
            "translation": "here",
            "example": "Je habite ici.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "étudiante",
            "translation": "student (female)",
            "example": "L'étudiante étudie à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "travaille",
            "translation": "work",
            "example": "Je travaille à l'hôtel.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "habites",
            "translation": "live (you)",
            "example": "Tu habites où?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "habite",
            "translation": "live",
            "example": "J'habite à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "étudie",
            "translation": "study",
            "example": "J'étudie à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "à",
            "translation": "at/to",
            "example": "Je vais à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "américaine",
            "translation": "American (female)",
            "example": "Elle est américaine.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "mexicain",
            "translation": "Mexican (male)",
            "example": "Il est mexicain.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "mexicaine",
            "translation": "Mexican (female)",
            "example": "Elle est mexicaine.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "américain",
            "translation": "American (male)",
            "example": "Il est américain.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "espagnol",
            "translation": "Spanish (male)",
            "example": "Il est espagnol.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "espagnole",
            "translation": "Spanish (female)",
            "example": "Elle est espagnole.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "parles",
            "translation": "speak (you)",
            "example": "Tu parles français?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "comment tu t'appelles",
            "translation": "what's your name",
            "example": "Comment tu t'appelles?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "excuse-moi",
            "translation": "excuse me",
            "example": "Excuse-moi, où est l'hôtel?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "française",
            "translation": "French (female)",
            "example": "Elle est française.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "anglaise",
            "translation": "English (female)",
            "example": "Elle est anglaise.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "s'appelle",
            "translation": "is called",
            "example": "Il s'appelle Jean.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "il",
            "translation": "he",
            "example": "Il habite à Paris.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "elle",
            "translation": "she",
            "example": "Elle étudie à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "an",
            "translation": "year",
            "example": "J'ai vingt ans.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "anglais",
            "translation": "English (male)",
            "example": "Il est anglais.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "parle",
            "translation": "speak",
            "example": "Je parle français.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "ai",
            "translation": "have (I)",
            "example": "J'ai un chat.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "français",
            "translation": "French (male)",
            "example": "Il est français.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "est",
            "translation": "is",
            "example": "Il est étudiant.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "bonne nuit",
            "translation": "good night",
            "example": "Bonne nuit!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "à demain",
            "translation": "see you tomorrow",
            "example": "À demain!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "bonne soirée",
            "translation": "good evening",
            "example": "Bonne soirée!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "eau",
            "translation": "water",
            "example": "Je bois de l'eau.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "beaucoup",
            "translation": "a lot",
            "example": "Merci beaucoup!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "au",
            "translation": "to the",
            "example": "Je vais au restaurant.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "bonne journée",
            "translation": "good day",
            "example": "Bonne journée!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "enchanté",
            "translation": "nice to meet you",
            "example": "Enchanté!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "au revoir",
            "translation": "goodbye",
            "example": "Au revoir!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "à bientôt",
            "translation": "see you soon",
            "example": "À bientôt!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "bienvenue",
            "translation": "welcome",
            "example": "Bienvenue!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "toi",
            "translation": "you",
            "example": "Comment ça va, toi?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "salut",
            "translation": "hi",
            "example": "Salut!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "bonsoir",
            "translation": "good evening",
            "example": "Bonsoir!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "très",
            "translation": "very",
            "example": "Très bien!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "merci",
            "translation": "thank you",
            "example": "Merci beaucoup!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "bien",
            "translation": "well",
            "example": "Ça va bien!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "bonjour",
            "translation": "hello",
            "example": "Bonjour!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "comment",
            "translation": "how",
            "example": "Comment ça va?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "ou",
            "translation": "or",
            "example": "Tu veux du café ou du thé?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "ça",
            "translation": "that/this",
            "example": "Ça va bien!",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "oui",
            "translation": "yes",
            "example": "Oui, je parle français.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "ça va",
            "translation": "how are you/it's okay",
            "example": "Ça va?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "pizza",
            "translation": "pizza",
            "example": "Je mange une pizza.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "croissant",
            "translation": "croissant",
            "example": "Je mange un croissant.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "manges",
            "translation": "eat (you)",
            "example": "Tu manges quoi?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "orange",
            "translation": "orange",
            "example": "Je mange une orange.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "mange",
            "translation": "eat",
            "example": "Je mange une pizza.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "tu",
            "translation": "you",
            "example": "Tu habites où?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "cheval",
            "translation": "horse",
            "example": "Le cheval est un animal de compagnie.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "chien",
            "translation": "dog",
            "example": "J'ai un chien.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "c'est",
            "translation": "it is",
            "example": "C'est un chat.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "es",
            "translation": "are (you)",
            "example": "Tu es étudiant?",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "fille",
            "translation": "girl",
            "example": "La fille étudie à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "je",
            "translation": "I",
            "example": "Je suis étudiant.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "suis",
            "translation": "am",
            "example": "Je suis français.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "femme",
            "translation": "woman",
            "example": "La femme travaille à l'hôtel.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "une",
            "translation": "a/an (feminine)",
            "example": "Une femme habite ici.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "garçon",
            "translation": "boy",
            "example": "Le garçon va à l'université.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "et",
            "translation": "and",
            "example": "Je mange une pizza et un croissant.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "homme",
            "translation": "man",
            "example": "L'homme travaille à l'aéroport.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "chat",
            "translation": "cat",
            "example": "J'ai un chat.",
            "learned": False
        },
        {
            "user_id": user_id,
            "word": "un",
            "translation": "a/an (masculine)",
            "example": "Un homme habite ici.",
            "learned": False
        }
    ]
    
    try:
        print(f"📝 Inserting {len(custom_words)} custom French words for user {user_id}...")
        
        # Insert all words at once
        response = supabase_admin.table("known_words").insert(custom_words).execute()
        
        print(f"✅ Successfully inserted {len(response.data)} words")
        
        # Show some examples
        print("\n📚 Sample words added:")
        for i, word in enumerate(response.data[:10]):
            print(f"   {i+1}. {word['word']} ({word['translation']})")
        
        if len(response.data) > 10:
            print(f"   ... and {len(response.data) - 10} more words")
            
        print(f"\n🎯 Custom words ready! You can now test with your React UI.")
        print(f"   User ID: {user_id}")
        print(f"   Total words: {len(response.data)}")
            
    except Exception as e:
        print(f"❌ Failed to insert words: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate known_words table with custom French words")
    parser.add_argument("--user-id", required=True, help="Firebase user ID to populate data for")
    
    args = parser.parse_args()
    
    print("🚀 FreeLingo Custom Words Populator")
    print("=" * 40)
    
    populate_custom_words(args.user_id)
    
    print("\n📋 Next steps:")
    print("   1. Start your React UI")
    print("   2. Log in with Google Auth")
    print("   3. Navigate to the words management page")
    print("   4. Test the dialogue feature with your known words") 