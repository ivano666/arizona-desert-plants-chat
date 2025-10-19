# Arizona Desert Plants Assistant

## Introduction

The Arizona Desert Plants Assistant is a Retrieval-Augmented Generation (RAG) application designed to help plant enthusiasts, homeowners, and landscaping professionals learn about and successfully cultivate the extensive variety of plants in the Sonoran Desert. By combining scientific botanical knowledge with practical Arizona-specific growing advice, this system intents to provide authoritative, context-aware answers to questions about desert plant care, identification, and landscaping.

## Problem Statement

Desert gardening in Arizona presents unique challenges that generic plant care resources fail to address. Phoenix and Tucson gardeners face extreme heat, minimal rainfall, alkaline soils, and intense UV exposure. Traditional plant databases either lack regional specificity or fail to integrate scientific knowledge with practical cultivation advice. There is a need for an intelligent system that can answer both "What is this plant?" and "How do I successfully grow it in Phoenix's harsh climate?"

## Objectives

### Primary Objectives

1. **Plant Identification & Discovery**
   - Enable users to identify desert plants by common or scientific names
   - Provide comprehensive information about plant characteristics, native habitats, and taxonomic classification
   - Help users discover suitable plants for their specific needs

2. **Arizona-Specific Care Guidance**
   - Deliver region-specific cultivation instructions tailored to Phoenix and Tucson climates
   - Provide guidance on watering schedules, soil preparation, sun exposure, and seasonal care
   - Offer advice on transplanting and establishing desert-adapted plants

3. **Landscaping & Plant Selection Support**
   - Assist homeowners and professionals in selecting appropriate native and adapted plants for xeriscaping projects
   - Recommend plant combinations and companion planting strategies
   - Support water-wise landscape design decisions

4. **Troubleshooting & Problem Diagnosis**
   - Help diagnose common plant health issues, pest problems, and environmental stress
   - Provide solutions specific to Arizona desert conditions
   - Answer seasonal care questions (monsoon preparation, frost protection, summer stress management)

## Target Users

- **Homeowners**: Planning or maintaining desert-friendly landscapes and seeking water-wise plant options
- **Gardening Enthusiasts**: Growing desert plants and cacti collections, seeking care advice
- **Landscaping Professionals**: Designing xeriscapes for clients and selecting appropriate plant palettes
- **Students & Educators**: Learning about Sonoran Desert ecology and native plant communities
- **Native Plant Advocates**: Promoting sustainable, water-conscious gardening practices

## Use Cases & Example Queries

The system is designed to handle diverse query types:

**Identification & Information:**
- "What is a palo verde tree and where does it grow naturally?"
- "Tell me about saguaro cactus characteristics"
- "What's the difference between agave and yucca plants?"

**Care & Cultivation:**
- "How often should I water a newly planted mesquite tree?"
- "What type of soil do barrel cacti need?"
- "When should I fertilize desert plants in Arizona?"

**Selection & Planning:**
- "What cacti can survive full Phoenix summer sun?"
- "What are good companion plants for agaves?"
- "What native plants attract hummingbirds and pollinators?"

**Troubleshooting:**
- "Why are my palo verde's leaves turning yellow?"
- "How do I protect my cacti from frost damage?"
- "What causes brown tips on agave leaves?"

## Value Proposition

Unlike generic plant databases or general gardening chatbots, the Arizona Desert Plants Assistant uniquely combines:

- **Scientific Accuracy**: Taxonomic data and botanical descriptions from verified sources (iNaturalist, Wikipedia)
- **Regional Expertise**: Arizona-specific care instructions from University of Arizona Cooperative Extension publications
- **Contextual Intelligence**: RAG architecture that retrieves relevant information and generates coherent, contextually appropriate answers
- **Practical Focus**: Real-world cultivation advice tested in Arizona's extreme desert climate

This integration of scientific knowledge with regional expertise makes the system invaluable for anyone gardening in the Sonoran Desert.

## Dataset Overview

The knowledge base consists of high-quality, authoritative sources:

**1. iNaturalist Species Database (340 species)**
- Research-grade plant observations from Arizona
- Scientific and common names with full taxonomic classification
- Wikipedia summaries providing botanical descriptions and characteristics
- Conservation status and native/introduced designations

**2. University of Arizona Cooperative Extension Publications (~14 documents)**
- Expert-reviewed care guides and cultivation instructions
- Desert landscaping and xeriscaping best practices
- Plant selection guides for Arizona conditions
- Specific care sheets for common desert plants (cacti, agaves, native trees)
- Watering, fertilizing, and seasonal maintenance guidelines

**Total Dataset**: ~400,000 characters of curated, Arizona-focused content combining scientific rigor with practical expertise.

## Technical Approach

This project implements a complete RAG pipeline including:
- Data collection and curation from multiple authoritative sources
- Text extraction and preprocessing for optimal retrieval
- Vector embeddings for semantic search
- LLM-powered response generation with source attribution
- Evaluation metrics to ensure answer quality and relevance

## Expected Impact

By providing accessible, accurate, and regionally appropriate plant information, this assistant will:
- Empower Arizona residents to make informed plant selection decisions
- Reduce plant mortality through proper care guidance
- Promote water-wise landscaping and native plant usage
- Support sustainable desert gardening practices
- Make expert horticultural knowledge accessible to all skill levels

## Setup
An OPENAI API key is required:
1. Since we are using OpenAI, it is a good practice to create a new project and key
2. Install direnv for your operating system - [link](https://direnv.net/docs/installation.html)
    1. Follow the **basic installation** instructions as well as **how to hook onto your shell**
    2. The quick demo section shows an example on how to create an env variable


## Data Preparation

## Data Ingestion

## 
