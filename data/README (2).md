# NLP News Pipeline 📰

A comprehensive Natural Language Processing pipeline for analyzing news articles, implementing various NLP techniques from text preprocessing to advanced topic modeling.

## 🎯 Project Overview

This project demonstrates a complete NLP workflow applied to news article data, covering fundamental to advanced techniques in natural language processing. The pipeline processes news articles through multiple stages to extract insights, find similarities, and discover underlying topics.

## ✨ Features

### 1. **Text Preprocessing**
- Text normalization (lowercase conversion)
- Special character removal
- Tokenization using NLTK
- Stopword removal
- Lemmatization with WordNet

### 2. **Text Representation (TF-IDF)**
- Term Frequency-Inverse Document Frequency vectorization
- Feature extraction from preprocessed text
- Article similarity computation using cosine similarity
- Top-5 related articles identification for each document

### 3. **Word Embeddings (Word2Vec)**
- Custom Word2Vec model training
- 100-dimensional word vectors
- Semantic word similarity analysis
- 2D visualization using PCA

### 4. **Language Modeling (N-gram)**
- Bigram-based next word prediction
- Probability distribution calculation
- Interactive word prediction function

### 5. **Topic Modeling (LDA)**
- Latent Dirichlet Allocation with 5 topics
- Automatic topic discovery from news corpus
- Document-topic distribution analysis
- Top keywords extraction for each topic

## 📊 Dataset

The project uses `Articles.csv` containing news articles with the following structure:
- **Heading**: Article headlines
- **Article**: Full article text
- **Total Articles**: 2,692 news articles

## 🛠️ Technologies Used

- **Python 3.x**
- **Libraries**:
  - `pandas` - Data manipulation
  - `nltk` - Natural language processing
  - `scikit-learn` - Machine learning algorithms (TF-IDF, LDA, PCA)
  - `gensim` - Word2Vec implementation
  - `matplotlib` - Data visualization
  - `numpy` - Numerical computing

## 📋 Requirements

```bash
pip install pandas nltk scikit-learn gensim matplotlib numpy
```

### NLTK Data Downloads
```python
import nltk
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
```

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NLP-News_Pipeline
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the notebook**
   ```bash
   jupyter notebook nlp_news_pipeline.ipynb
   ```

## 📈 Pipeline Workflow

```
Raw Text → Preprocessing → TF-IDF Vectorization → Article Similarity
                ↓
         Word Embeddings (Word2Vec) → Semantic Analysis
                ↓
         N-gram Model → Next Word Prediction
                ↓
         Topic Modeling (LDA) → Topic Discovery
```

## 🔍 Key Results

### Word2Vec Similarity Example
For the word "market", the most similar words are:
- global (0.91)
- analyst (0.88)
- commodity (0.88)
- weak (0.88)
- investor (0.88)

### Discovered Topics (Sample)
1. **Topic 1**: Finance & Economy - percent, price, oil, market, crude, dollar, barrel, rate, stock, bank
2. **Topic 2**: Sports (Cricket) - pakistan, test, england, cricket, first, india, team, wicket, run
3. **Topic 3**: Business & Technology - car, apple, billion, vehicle, emission, map, broadband
4. **Topic 4**: Media & Lifestyle - restaurant, cyber, sec
5. **Topic 5**: Mixed Topics - Various business and technology terms

## 📝 Code Structure

```
NLP-News_Pipeline/
│
├── nlp_news_pipeline.ipynb    # Main Jupyter notebook
├── Articles.csv                # News articles dataset
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Complete NLP preprocessing pipeline
- ✅ Text vectorization techniques
- ✅ Semantic similarity computation
- ✅ Word embedding generation and visualization
- ✅ Statistical language modeling
- ✅ Unsupervised topic discovery

## 🔧 Customization

You can customize the pipeline by:
- Adjusting Word2Vec parameters (vector_size, window, min_count)
- Changing the number of topics in LDA
- Modifying n-gram order (currently bigram)
- Adding additional preprocessing steps
- Experimenting with different similarity metrics

## 📊 Visualizations

The project includes:
- Word embedding visualization using PCA
- Topic distribution analysis
- Article similarity matrices

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

Created as a demonstration of NLP techniques for news article analysis.

## 🙏 Acknowledgments

- NLTK team for comprehensive NLP tools
- Gensim developers for Word2Vec implementation
- Scikit-learn for machine learning utilities

---

**Note**: This project is designed for educational purposes to demonstrate various NLP techniques in a practical application.
