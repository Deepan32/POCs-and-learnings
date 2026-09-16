from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace, RoleChecker
from backend.app.models.workspace import Workspace, RoleEnum
from backend.app.models.product import ProductService
from backend.app.models.quick_reply import QuickReply
from backend.app.models.automation import AutomationRule

router = APIRouter()

INDUSTRY_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "florist-wings-flower",
        "name": "Wings Flower — Florist & Gifts",
        "category": "Retail / Florist",
        "icon": "Flower2",
        "description": "Complete setup for flower boutiques, bouquet deliveries, wedding floral arrangements, and gift hampers.",
        "primary_color": "#E11D48",
        "secondary_color": "#BE123C",
        "greeting_message": "🌸 Welcome to Wings Flower! How can we brighten your day? Reply 1 for Fresh Bouquets, 2 for Wedding Decor, or 3 to speak with our floral designer.",
        "products": [
            {"name": "Royal Velvet Rose Bouquet (12 Stems)", "category": "Bouquets", "price": 1499.0, "description": "Premium Dutch red roses hand-tied in imported kraft wrap with satin ribbon.", "sku": "WF-ROSE-12"},
            {"name": "Pastel Lily & Carnation Symphony", "category": "Bouquets", "price": 1899.0, "description": "Fragrant pink Asiatic lilies combined with pastel carnations and baby's breath.", "sku": "WF-LILY-01"},
            {"name": "Midnight Orchid Luxury Box", "category": "Luxury Arrangements", "price": 2499.0, "description": "Fresh purple dendrobium orchids presented in a matte black velvet keepsake cylinder.", "sku": "WF-ORC-BOX"},
            {"name": "Bespoke Wedding Mandap Floral Package", "category": "Events & Decor", "price": 45000.0, "description": "Full stage, aisle, and mandap fresh floral styling customized to your palette.", "sku": "WF-WED-FULL"},
            {"name": "Gourmet Chocolates & Ferrero Hamper Addon", "category": "Add-ons", "price": 799.0, "description": "Assorted artisan chocolates and Ferrero Rocher box paired with flowers.", "sku": "WF-ADD-CHOC"}
        ],
        "quick_replies": [
            {"shortcut": "/catalog", "title": "Send Flower Catalog", "message": "💐 View our current seasonal flower catalog with price list here: https://wingsflower.store/catalog", "category": "Catalog"},
            {"shortcut": "/delivery", "title": "Delivery Areas & Slots", "message": "🚚 We offer same-day express delivery within 2 hours across the city! Morning slot: 9am-1pm, Evening slot: 4pm-9pm.", "category": "Delivery"},
            {"shortcut": "/custom", "title": "Custom Arrangement", "message": "✨ Want a personalized bouquet? Share your budget and flower preference, and our head florist will craft a preview for you!", "category": "Custom Orders"},
            {"shortcut": "/timing", "title": "Store Timings & Location", "message": "📍 Wings Flower Boutique is open 7 days a week from 8:00 AM to 10:00 PM. We look forward to your visit!", "category": "Location"}
        ],
        "lead_stages": ["New Inquiry", "Selected Bouquet", "Address Received", "Payment Pending", "Delivered & Delighted"]
    },
    {
        "id": "restaurant-cafe",
        "name": "Urban Bistro & Cafe",
        "category": "Hospitality / F&B",
        "icon": "UtensilsCrossed",
        "description": "WhatsApp ordering, table reservations, digital menu broadcasting, and party catering bookings.",
        "primary_color": "#D97706",
        "secondary_color": "#B45309",
        "greeting_message": "🍽️ Welcome to Urban Bistro! Craving something delicious? Reply with MENU to view digital menu, TABLE to reserve seats, or PARTY for catering.",
        "products": [
            {"name": "Artisanal Woodfired Margherita Pizza", "category": "Mains", "price": 480.0, "description": "San Marzano tomatoes, buffalo mozzarella, fresh basil, extra virgin olive oil.", "sku": "UB-PIZZA-01"},
            {"name": "Truffle Mushroom Risotto", "category": "Mains", "price": 560.0, "description": "Arborio rice slow-cooked with wild porcini mushrooms, parmesan and truffle oil.", "sku": "UB-RISO-02"},
            {"name": "Espresso Tonic & Cold Brew Float", "category": "Beverages", "price": 220.0, "description": "Single-origin Arabica 18-hour cold brew over artisanal tonic and gelato.", "sku": "UB-BEV-03"},
            {"name": "Weekend Chef's Tasting Menu (2 Pax)", "category": "Specials", "price": 2200.0, "description": "5-course curated dining experience paired with non-alcoholic botanical blends.", "sku": "UB-SPEC-05"}
        ],
        "quick_replies": [
            {"shortcut": "/menu", "title": "Digital Food Menu", "message": "📖 Explore our live digital menu with images and chef specials: https://urbanbistro.order/menu", "category": "Menu"},
            {"shortcut": "/reserve", "title": "Table Reservation Link", "message": "🪑 To reserve a table, please tell us: Date, Time, and Number of Guests. We will confirm your table in 5 minutes!", "category": "Reservations"},
            {"shortcut": "/hours", "title": "Kitchen & Dining Hours", "message": "⏰ We serve lunch 12:00 PM - 3:30 PM and dinner 7:00 PM - 11:30 PM. Valet parking is available!", "category": "Info"}
        ],
        "lead_stages": ["Inquiry", "Table Reserved", "Dined In", "Feedback Collected", "VIP Regular"]
    },
    {
        "id": "clinic-healthcare",
        "name": "CarePlus Medical & Dental",
        "category": "Healthcare / Clinic",
        "icon": "Stethoscope",
        "description": "Doctor appointment booking, tele-consultation reminders, lab report delivery, and patient intake.",
        "primary_color": "#0284C7",
        "secondary_color": "#0369A1",
        "greeting_message": "🩺 Welcome to CarePlus Clinic. How may we assist you today? 1. Book Appointment 2. Get Lab Reports 3. Emergency Support.",
        "products": [
            {"name": "Comprehensive Dental Consultation & X-Ray", "category": "Dental", "price": 600.0, "description": "Full oral examination, digital intraoral sensor X-ray, and personalized hygiene plan.", "sku": "CP-DENT-01"},
            {"name": "Full Body Wellness Health Package (56 Tests)", "category": "Diagnostics", "price": 1999.0, "description": "CBC, Lipid profile, Liver function, Kidney function, Vitamin D3/B12, and HbA1c.", "sku": "CP-LAB-56"},
            {"name": "Physician Video Consultation (30 mins)", "category": "Telehealth", "price": 500.0, "description": "Secure 1-on-1 tele-consultation with our Senior General Physician.", "sku": "CP-TELE-01"}
        ],
        "quick_replies": [
            {"shortcut": "/book", "title": "Book Doctor Appointment", "message": "📅 To book an appointment, please share patient name, age, preferred department, and convenient date/slot.", "category": "Appointments"},
            {"shortcut": "/reports", "title": "Lab Report Status", "message": "📋 Your lab reports will be automatically sent to this WhatsApp number as soon as our pathologist signs off!", "category": "Reports"},
            {"shortcut": "/location", "title": "Clinic Address & Map", "message": "📍 CarePlus Clinic, 4th Cross Road, Near Central Park. Google Maps: https://maps.app/careplus", "category": "Location"}
        ],
        "lead_stages": ["New Patient", "Slot Requested", "Appointment Confirmed", "Consultation Done", "Follow-up Due"]
    },
    {
        "id": "salon-spa",
        "name": "Glow & Co. Salon & Spa",
        "category": "Beauty & Wellness",
        "icon": "Sparkles",
        "description": "Salon appointments, bridal packages, stylist allocations, loyalty offers, and post-service follow-up.",
        "primary_color": "#EC4899",
        "secondary_color": "#DB2777",
        "greeting_message": "✨ Welcome to Glow & Co.! Ready to pamper yourself? Reply 1 for Hair & Styling, 2 for Skin & Spa, 3 for Bridal Packages.",
        "products": [
            {"name": "Moroccan Argan Hair Spa Treatment", "category": "Hair", "price": 1800.0, "description": "Deep nourishment with authentic Argan steam infusion, scalp massage, and blowdry.", "sku": "GC-SPA-01"},
            {"name": "Hydra-Radiance Facial & Collagen Boost", "category": "Skin", "price": 2500.0, "description": "Multi-step gentle suction exfoliation, ultrasound hydration, and cooling sheet mask.", "sku": "GC-FACE-02"},
            {"name": "Luxury Bridal Makeover & Hair Design", "category": "Bridal", "price": 15000.0, "description": "HD airbrush makeup, saree draping, floral hair updo, and pre-bridal consultation.", "sku": "GC-BRIDE-01"}
        ],
        "quick_replies": [
            {"shortcut": "/book", "title": "Book Appointment", "message": "💆‍♀️ Let us know your preferred stylist, service, date and time to reserve your pampering session!", "category": "Booking"},
            {"shortcut": "/packages", "title": "Bridal & Party Combos", "message": "👰 Explore our seasonal combo packages and group bridal discounts here: https://glowandco.salon/deals", "category": "Offers"}
        ],
        "lead_stages": ["Inquiry", "Slot Selected", "Confirmed", "Service Completed", "Review Requested"]
    },
    {
        "id": "edtech-coaching",
        "name": "Apex Learning Academy",
        "category": "Education / Coaching",
        "icon": "GraduationCap",
        "description": "Student course inquiries, batch schedule demos, syllabus downloads, fee collection, and exam alerts.",
        "primary_color": "#2563EB",
        "secondary_color": "#1D4ED8",
        "greeting_message": "🎓 Welcome to Apex Academy! What are you aspiring to learn? 1. Full Stack AI & Web 2. Data Science 3. Speak to an Admissions Counselor.",
        "products": [
            {"name": "Full Stack AI & Web Development Bootcamp (16 Weeks)", "category": "Certifications", "price": 45000.0, "description": "Live interactive training in Python, FastAPI, Next.js, LLMs, and real-world projects with placement assistance.", "sku": "APX-FS-AI"},
            {"name": "Data Analytics & PowerBI Masterclass", "category": "Short Courses", "price": 14999.0, "description": "SQL, Python pandas, PowerBI dashboarding, and business intelligence portfolio.", "sku": "APX-DA-BI"}
        ],
        "quick_replies": [
            {"shortcut": "/syllabus", "title": "Download Course Syllabus", "message": "📚 Download the complete weekly curriculum and capstone project list here: https://apex.edu/syllabus", "category": "Curriculum"},
            {"shortcut": "/demo", "title": "Free Live Demo Class", "message": "🚀 We hold a free live masterclass this Saturday at 6:00 PM! Reply YES to secure your seat.", "category": "Demo"}
        ],
        "lead_stages": ["Lead Inquired", "Syllabus Downloaded", "Attended Demo", "Fee Quote Sent", "Enrolled"]
    },
    {
        "id": "real-estate",
        "name": "Skyline Realty & Spaces",
        "category": "Real Estate / Property",
        "icon": "Building2",
        "description": "Property site visit bookings, brochure downloads, floor plan sharing, and buyer budget qualification.",
        "primary_color": "#0F766E",
        "secondary_color": "#115E59",
        "greeting_message": "🏢 Welcome to Skyline Realty! Finding your dream home is just a message away. Reply 1 for 2 & 3 BHK Luxury Apartments, 2 for Gated Villas, 3 to Schedule a Site Visit.",
        "products": [
            {"name": "Skyline Heights - 3 BHK Premium Golf Facing", "category": "Luxury Apartments", "price": 12500000.0, "description": "1850 sq.ft, Italian marble flooring, 3 balconies, 2 parking slots, possession Q4 2026.", "sku": "SKY-3BHK-GOLF"},
            {"name": "The Palms Gated Villa (4 BHK with Private Pool)", "category": "Villas", "price": 27500000.0, "description": "3400 sq.ft built-up area, private plunge pool, terrace garden, and smart home automation.", "sku": "SKY-VILLA-04"}
        ],
        "quick_replies": [
            {"shortcut": "/brochure", "title": "Project Brochure PDF", "message": "📄 Download the Skyline Heights master plan, floor plans, and amenities brochure: https://skyline.estate/brochures", "category": "Brochure"},
            {"shortcut": "/visit", "title": "Schedule Site Visit", "message": "🚗 We provide complimentary cab pickup for site visits on weekends! Share your convenient date and time.", "category": "Site Visit"}
        ],
        "lead_stages": ["New Lead", "Budget Verified", "Brochure Sent", "Site Visit Scheduled", "Deal Closed"]
    },
    {
        "id": "ecommerce-d2c",
        "name": "TrendStreet D2C Apparel",
        "category": "E-Commerce / D2C",
        "icon": "ShoppingBag",
        "description": "Order tracking, COD confirmation, return/exchange automation, flash sale broadcasting, and cart recovery.",
        "primary_color": "#8B5CF6",
        "secondary_color": "#7C3AED",
        "greeting_message": "🛍️ Hey there, style icon! Welcome to TrendStreet. Reply TRACK with your Order ID to see delivery status, or NEW to see this week's drop!",
        "products": [
            {"name": "Heavyweight Oversized Boxy Tee (260 GSM)", "category": "Apparel", "price": 999.0, "description": "100% combed French Terry cotton, drop shoulder, acid-wash finish.", "sku": "TS-TEE-BOX"},
            {"name": "Everyday Relaxed Cargo Pants", "category": "Bottoms", "price": 1899.0, "description": "6 utility pockets, adjustable ankle toggles, waterproof ripstop fabric.", "sku": "TS-CARGO-01"}
        ],
        "quick_replies": [
            {"shortcut": "/track", "title": "Track Live Order", "message": "📦 Share your 6-digit Order ID (e.g. #TS1092) and we'll pull your live courier tracking link immediately!", "category": "Orders"},
            {"shortcut": "/exchange", "title": "Exchange & Returns", "message": "🔄 We offer hassle-free 7-day doorstep size exchanges. Visit https://trendstreet.in/returns to initiate.", "category": "Support"}
        ],
        "lead_stages": ["Website Visitor", "Abandoned Cart", "Order Placed", "Shipped", "Repeat Buyer"]
    },
    {
        "id": "b2b-saas-services",
        "name": "ScaleOps Growth & Consulting",
        "category": "B2B / Tech Services",
        "icon": "Briefcase",
        "description": "B2B lead qualification, discovery call bookings, portfolio sharing, case study distribution, and SLA support.",
        "primary_color": "#3B82F6",
        "secondary_color": "#1D4ED8",
        "greeting_message": "💼 Welcome to ScaleOps! We help high-growth companies scale engineering and revenue operations. Reply 1 for Case Studies, 2 for Pricing, 3 to Book a 15-min Discovery Call.",
        "products": [
            {"name": "AI Automation & Workflow Architecture Audit", "category": "Consulting", "price": 35000.0, "description": "Comprehensive 2-week architectural assessment of your existing CRM, WhatsApp, and API pipelines.", "sku": "SO-AUDIT-01"},
            {"name": "Dedicated Full-Stack Pod (Monthly Retainer)", "category": "Engineering", "price": 180000.0, "description": "Senior Python + Next.js engineer and DevOps lead dedicated to your product velocity.", "sku": "SO-POD-MO"}
        ],
        "quick_replies": [
            {"shortcut": "/calendar", "title": "Book Discovery Call", "message": "🗓️ Schedule a 15-minute intro with our Solutions Architect here: https://cal.com/scaleops/discovery", "category": "Meetings"},
            {"shortcut": "/casestudies", "title": "Client Case Studies", "message": "📊 Read how we helped a FinTech client scale to 2M monthly active transactions: https://scaleops.io/cases", "category": "Portfolio"}
        ],
        "lead_stages": ["Qualified Lead", "Discovery Scheduled", "Proposal Sent", "Contract Review", "Won / Onboarding"]
    }
]

@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_industry_templates():
    return INDUSTRY_TEMPLATES

@router.post("/templates/{template_id}/apply")
async def apply_industry_template(
    template_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    target = next((t for t in INDUSTRY_TEMPLATES if t["id"] == template_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Industry template not found")

    # 1. Update branding & colors
    workspace.primary_color = target["primary_color"]
    workspace.secondary_color = target["secondary_color"]
    workspace.industry = target["category"]

    # 2. Add products
    for p in target["products"]:
        # Check if already exists by sku or name
        exists = (await db.execute(
            select(ProductService).where(
                ProductService.workspace_id == workspace.id,
                ProductService.name == p["name"]
            )
        )).scalars().first()
        if not exists:
            db.add(ProductService(
                workspace_id=workspace.id,
                name=p["name"],
                description=p["description"],
                category=p["category"],
                price=p["price"],
                currency="INR",
                sku=p.get("sku"),
                is_available=True
            ))

    # 3. Add quick replies
    for qr in target["quick_replies"]:
        exists_qr = (await db.execute(
            select(QuickReply).where(
                QuickReply.workspace_id == workspace.id,
                QuickReply.shortcut == qr["shortcut"]
            )
        )).scalars().first()
        if not exists_qr:
            db.add(QuickReply(
                workspace_id=workspace.id,
                shortcut=qr["shortcut"],
                title=qr["title"],
                message=qr["message"],
                category=qr["category"]
            ))

    # 4. Create or update a Welcome greeting rule if not exists
    rule_exists = (await db.execute(
        select(AutomationRule).where(
            AutomationRule.workspace_id == workspace.id,
            AutomationRule.trigger_keyword == "hi"
        )
    )).scalars().first()
    if not rule_exists:
        db.add(AutomationRule(
            workspace_id=workspace.id,
            name=f"{target['name']} Welcome Greeting",
            trigger_keyword="hi",
            match_type="contains",
            condition_contact_is_new=True,
            action_reply_text=target["greeting_message"],
            is_active=True,
            priority=10
        ))

    await db.commit()
    await db.refresh(workspace)

    return {
        "message": f"Successfully applied template '{target['name']}' to client workspace!",
        "products_added": len(target["products"]),
        "quick_replies_added": len(target["quick_replies"])
    }
