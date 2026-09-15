import json
import logging
from typing import List, Dict, Any
from backend.app.database.database import init_db
from backend.app.rag.vector_store import vector_store

logger = logging.getLogger(__name__)

KNOWLEDGE_CHUNKS: List[Dict[str, Any]] = [
    {
        "parameter": "pH",
        "topic": "Soil Acidity & Reaction",
        "title": "Soil Acidity and Liming: Interpreting Soil pH",
        "organization": "Penn State Extension",
        "source": "Penn State Extension Soil Guide (2023)",
        "page": 4,
        "section": "Soil Reaction and Nutrient Availability",
        "content": "Soil pH measures hydrogen ion activity. Most garden vegetables and agronomic crops thrive between pH 6.0 and 6.8. When pH falls below 5.5, availability of macronutrients like phosphorus, calcium, and magnesium is sharply restricted, while toxic soluble aluminum (Al3+) and manganese ions increase."
    },
    {
        "parameter": "CEC",
        "topic": "Cation Exchange Capacity",
        "title": "Cation Exchange Capacity in Soils",
        "organization": "Iowa State University Extension and Outreach",
        "source": "Iowa State Extension Encyclopedia (2022)",
        "page": 2,
        "section": "Cation Exchange Capacity Interpretation",
        "content": "Cation Exchange Capacity (CEC) reflects the soil's reservoir capacity to retain positively charged nutrient cations (Ca2+, Mg2+, K+, NH4+). Sandy soils typically exhibit CEC values below 10 meq/100g, requiring split nutrient applications to prevent leaching, whereas loam and clay soils range between 10 and 25 meq/100g."
    },
    {
        "parameter": "Organic Matter",
        "topic": "Soil Organic Matter & Soil Health",
        "title": "Comprehensive Assessment of Soil Health: Soil Organic Matter",
        "organization": "Cornell University Cooperative Extension",
        "source": "Cornell Soil Health Manual (2021)",
        "page": 18,
        "section": "Organic Matter Benchmarks",
        "content": "Soil Organic Matter (SOM) provides water retention, biological habitat, and mineralizable nitrogen and sulfur. For mineral agricultural soils, 3.0% to 5.0% SOM is considered optimal. Soils below 2.0% indicate depleted carbon reserves, degraded aggregate stability, and vulnerability to compaction."
    },
    {
        "parameter": "N",
        "topic": "Nitrogen Availability",
        "title": "Nitrogen Management in Field and Vegetable Soils",
        "organization": "Purdue University Extension",
        "source": "Purdue Extension Agronomy Guide (2022)",
        "page": 11,
        "section": "Available Nitrogen Dynamics",
        "content": "Nitrate-N represents immediately plant-available nitrogen essential for vegetative growth and chlorophyll synthesis. Adequate levels typically range from 25 to 50 ppm depending on crop demand. Deficiencies cause chlorosis and stunted shoot elongation."
    },
    {
        "parameter": "P",
        "topic": "Phosphorus Fertility",
        "title": "Understanding Soil Phosphorus and Potassium Fertility",
        "organization": "University of Minnesota Extension",
        "source": "UMN Extension Soil Fertility Series (2023)",
        "page": 7,
        "section": "Phosphorus Availability and Fixation",
        "content": "Soil phosphorus (P) is vital for early root elongation, ATP energy transfer, and seed set. In Bray-1 or Mehlich-3 extraction, optimum levels for vegetable crops fall between 15 and 30 ppm. Values below 14 ppm are deficient and severely limit early seedling vigor."
    },
    {
        "parameter": "K",
        "topic": "Potassium Fertility",
        "title": "Understanding Soil Phosphorus and Potassium Fertility",
        "organization": "University of Minnesota Extension",
        "source": "UMN Extension Soil Fertility Series (2023)",
        "page": 12,
        "section": "Potassium Cation Balance",
        "content": "Potassium (K) regulates plant stomatal conductance, water stress tolerance, and enzyme activation. Standard agronomic ranges span 100 to 160 ppm. Deficiencies below 100 ppm induce marginal leaf scorching, weak stems, and susceptibility to fungal pathogens."
    },
    {
        "parameter": "Ca",
        "topic": "Calcium and Base Saturation",
        "title": "Cation Exchange Capacity and Base Saturation",
        "organization": "Iowa State University Extension and Outreach",
        "source": "Iowa State Extension Soil Fertility (2022)",
        "page": 5,
        "section": "Calcium Cation Levels",
        "content": "Calcium (Ca) forms pectin structural complexes in plant cell walls and maintains soil flocculation. Optimal agricultural soil levels range from 1,000 to 1,500 ppm (65-75% base saturation). Levels below 500 ppm cause apical blossom end rot and cellular collapse in sensitive crops."
    },
    {
        "parameter": "Mg",
        "topic": "Magnesium Fertility",
        "title": "Secondary and Micronutrient Fertility Management",
        "organization": "Purdue University Extension",
        "source": "Purdue Extension Guide AY-239 (2022)",
        "page": 8,
        "section": "Magnesium Management",
        "content": "Magnesium (Mg) is the central coordinating atom in chlorophyll molecules. Desirable soil levels range from 50 to 120 ppm (10-15% base saturation). Deficiencies appear as interveinal chlorosis on older bottom leaves and impair photosynthetic capacity."
    },
    {
        "parameter": "S",
        "topic": "Sulfur Fertility",
        "title": "Secondary and Micronutrient Fertility Management",
        "organization": "Purdue University Extension",
        "source": "Purdue Extension Guide AY-239 (2022)",
        "page": 14,
        "section": "Sulfate-Sulfur Dynamics",
        "content": "Sulfur (S) is required for methionine and cysteine amino acid synthesis and protein formation. Sulfate-sulfur concentrations above 10 ppm are considered optimal. Because sulfate is an anion subject to leaching in sandy profiles, maintaining organic matter aids retention."
    },
    {
        "parameter": "B",
        "topic": "Boron Micronutrient",
        "title": "Micronutrients in Crop Production",
        "organization": "Purdue University Extension",
        "source": "Purdue Extension Guide AY-239 (2022)",
        "page": 19,
        "section": "Boron Availability",
        "content": "Boron (B) facilitates sugar translocation, cell wall development, and pollen tube growth. The narrow target range is 0.1 to 0.5 ppm. Values below 0.1 ppm cause hollow stem and poor fruit set, while values exceeding 2.0 ppm can cause severe leaf burn toxicity."
    },
    {
        "parameter": "Mn",
        "topic": "Manganese Micronutrient",
        "title": "Micronutrients in Crop Production",
        "organization": "Purdue University Extension",
        "source": "Purdue Extension Guide AY-239 (2022)",
        "page": 21,
        "section": "Manganese Soil Dynamics",
        "content": "Manganese (Mn) participates in water-splitting photosystem reactions and lignin synthesis. Optimum range is 1.1 to 6.3 ppm. Availability drops sharply above pH 6.8 and rises excessively in strongly acidic soils below pH 5.0."
    },
    {
        "parameter": "Zn",
        "topic": "Zinc Micronutrient",
        "title": "Micronutrients in Crop Production",
        "organization": "Purdue University Extension",
        "source": "Purdue Extension Guide AY-239 (2022)",
        "page": 24,
        "section": "Zinc Dynamics",
        "content": "Zinc (Zn) serves as an essential cofactor for auxin hormone synthesis and carbohydrate metabolism. Optimal levels range between 1.0 and 7.6 ppm. Deficiencies below 1.0 ppm manifest as shortened internodes (rosetting) and interveinal banding on corn and vegetable foliage."
    },
    {
        "parameter": "Cu",
        "topic": "Copper Micronutrient",
        "title": "Micronutrients in Crop Production",
        "organization": "Purdue University Extension",
        "source": "Purdue Extension Guide AY-239 (2022)",
        "page": 26,
        "section": "Copper Fertility",
        "content": "Copper (Cu) acts in plant respiration, photosynthetic electron transport, and reproductive seed set. Adequate soil levels are 0.3 to 0.6 ppm. Deficiencies occur predominantly on high organic peat soils."
    },
    {
        "parameter": "Fe",
        "topic": "Iron Availability",
        "title": "Micronutrients in Crop Production",
        "organization": "Purdue University Extension",
        "source": "Purdue Extension Guide AY-239 (2022)",
        "page": 28,
        "section": "Iron Soil Levels",
        "content": "Iron (Fe) is involved in chlorophyll synthesis and electron transfer. Agricultural sufficiency spans 2.7 to 9.4 ppm. High values above 50 ppm indicate acidic or waterlogged reducing conditions where iron becomes abundantly soluble."
    },
    {
        "parameter": "Al",
        "topic": "Aluminum Toxicity",
        "title": "Soil Acidity and Liming: Aluminum Toxicity Mechanisms",
        "organization": "Penn State Extension",
        "source": "Penn State Extension Soil Guide (2023)",
        "page": 7,
        "section": "Soluble Aluminum Constraints",
        "content": "Aluminum (Al) is not an essential plant nutrient. When soil pH drops below 5.0, structural aluminosilicates dissolve, releasing phytotoxic Al3+ ions. Levels above 75 ppm inhibit root cell division and stunt taproot elongation, precipitating drought and nutrient stress."
    },
    {
        "parameter": "Pb",
        "topic": "Lead and Heavy Metal Safety",
        "title": "Soil Quality - Heavy Metals and Urban Garden Soils",
        "organization": "USDA Natural Resources Conservation Service (NRCS)",
        "source": "USDA-NRCS Urban Soil Health Guide (2020)",
        "page": 6,
        "section": "Lead Safety Thresholds",
        "content": "Lead (Pb) is a persistent heavy metal contaminant with no biological function in plants. USDA-NRCS guidelines consider concentrations below 22 ppm safe and natural background. Levels between 100 and 400 ppm warrant raised beds and soil washing before vegetable consumption."
    },
    {
        "parameter": "EC",
        "topic": "Electrical Conductivity & Salinity",
        "title": "Soil Salinity and Electrical Conductivity",
        "organization": "University of Georgia Cooperative Extension",
        "source": "UGA Cooperative Extension Bulletin 1454 (2021)",
        "page": 3,
        "section": "Electrical Conductivity Indices",
        "content": "Electrical Conductivity (EC) measures soluble salt concentrations in soil solution. Normal nonsaline soils have EC below 1.0 dS/m. Values above 2.0 dS/m induce osmotic stress, restricting plant root water uptake."
    }
]

def ingest_knowledge_base():
    init_db()
    logger.info("Ingesting curated agricultural extension knowledge base...")
    vector_store.add_chunks(KNOWLEDGE_CHUNKS)
    print(f"Successfully ingested {len(KNOWLEDGE_CHUNKS)} chunks into vector store.")

if __name__ == "__main__":
    ingest_knowledge_base()
