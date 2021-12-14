def Data_Acquisition(url,params=None):
    if url== '':
        print('The data link is empty')
        return 
    else:
        request = requests.get(url, params)
        if request.status_code == 200:
            print('Successfully obtaining data')
            print('content-type:',request.headers['content-type'])
            return request.json(),request.headers['content-type']
        else:
            print('Failed to obtain data')
            
            
def xml2df(xmlFileName):
    with open(xmlFileName, 'r') as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        return pd.DataFrame(list(iter_records(root)))
 
def json2df(c_type,data):
    if 'json' in c_type:
        data = pd.DataFrame(data)
    return data

def Data_Cleaning(data):
    duplicate_data = data.loc[data.duplicated(subset=['name'],keep=False),:]
    print('Duplicated data:')
    display(duplicate_data)
    data.drop_duplicates(subset=['name'],keep=False,inplace=True) 
    print('Start processing the missing values')
    data.dropna(subset=['price','brand'],how='any',inplace=True)
    data.dropna(subset=['category','product_type'],how='all',inplace=True)
    data['price_sign'].fillna('$',inplace=True)
    data['currency'].fillna('USD',inplace=True)
    data['rating'].fillna(data.median()['rating'],inplace=True)
    data['description'].fillna('',inplace=True)
    data.drop(data[data.price<=0].index,inplace=True)
    return data
    
  def Currency_Exchange(data):
    request = requests.get('https://www.live-rates.com/rates')
    currency_dict = {'USD':1}
    if request.status_code == 200:
        print('Successfully obtaining data')
        print('content-type:',request.headers['content-type'])
        currency = request.json()
        currency_df = pd.DataFrame(currency)
        for cu in data.currency.unique():
            if cu!= 'USD':
                currency_rate = currency_df[currency_df.currency=='USD/'+cu]['rate']
                currency_dict[cu] = currency_rate.astype('float').values[0]
        data['currency_rate'] = data['currency'].map(currency_dict)
        data['price'] = data['price'].astype('float')
        data['price_USD'] = data['price'] / data['currency_rate']
        print(currency_dict)
    else:
        print('Failed to obtain data')
        
def NLP_pre_process(data):
    ## remove stop words in the textual descriptions. 
    data = data.copy()
    sw = set(stopwords.words("english"))
    for index,row in data.iterrows():
        txt = row['description']
        if txt == '':
            continue
        description = [i for i in txt.split() if i not in sw]
        description = ' '.join(description)
        ## stemming textual descriptions
        stemmer = PorterStemmer()
        tmp_txt = [stemmer.stem(word) for word in description.split()]
        tmp_txt = ' '.join(tmp_txt)
        data.loc[index,'description'] = tmp_txt
    return data
    
def Visualization(data):
    fig,ax = plt.subplots(2,2)
    sns.distplot(data['price'],ax=ax[0][0])
    sns.distplot(data['rating'],ax=ax[0][1])
    sns.countplot(data['product_type'],ax=ax[1][0])

def Product_screening(data):
    description = input('Please enter the product function/category: ')
    if description in data['category'].unique():
        data_s = data[data['category']==description]
    elif description in data['product_type'].unique():
        data_s = data[data['product_type']==description]
    else:          
        data_s = pd.DataFrame([])
    for index,row in data.iterrows():
        if re.search(description,row['description']) != None:
            data_s.append(data.loc[index])
    data_s.drop_duplicates(subset=['name'],keep=False,inplace=True) 
    if len(data_s)==0:
        print('No this product')
        return
    data_s.sort_values(by=['price_USD','rating'],ascending=[1,0],inplace=True)
    data_s.reset_index(inplace=True,drop=True)
    url = data_s.loc[0,'image_link']
    r = requests.get(url)
    print(r.status_code)
    path = 'E://python_project//product.jpg'
    with open(path,'wb') as f:
        f.write(r.content)
    f.close
    img = Image.open(path)
    plt.figure("Image")
    plt.imshow(img)
    plt.axis('off')
    plt.title('image')
    plt.show()
    return data_s.head(1)
    
def getAmazonSearch(search_query,headers):
    url='https://www.amazon.com/s?k='+search_query
    print(url)
    try:
        page=requests.get(url, headers=headers)
        page.raise_for_status()
        return page
    except:
        return 'Error'
        
 def Searchreviews(review_link):
    url="https://www.amazon.com"+review_link
    print(url)
    kv = {'User-Agent':'Mozilla/5.0'}
    page=requests.get(url, headers = (kv))
    if page.status_code==200:
        return page
    else:
        return "Error"    
        
def Searchasin(asin):
    url="https://www.amazon.com/dp/"+asin
    print(url)
    kv = {'User-Agent':'Mozilla/5.0'}
    page=requests.get(url, headers = (kv))
    if page.status_code==200:
        return page
    else:
        return "Error"  
        
def spyder_review(data):abs
    headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 Edg/96.0.1054.53',
                'cookie': 'aws-target-static-id=1571909168744-985449; s_dslv=1571909898041; aws-ubid-main=773-8777087-2750440; s_fid=29F4D0C5E949333F-0489987612FC0FDF; aws-business-metrics-last-visit=1571910150211; aws-priv=eyJ2IjoxLCJldSI6MCwic3QiOjB9; regStatus=registering; session-id=147-8255450-5756569; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:CN"; ubid-main=131-1709846-6781632; lc-main=en_US; session-token=UwFtAE4A5LofPdI7MEArKhUJuFye2LetT0r5qwpABvnKjBbe9f71RYE9XmUn4jwhZiNUqcbztUGimATC7zH33XHHwbO3A8UoonxMMAsIS+aLvwhWB7iEjNmgQjZSgzBo99+emRkReEhZgjxQ3/Gfj7hRbSE5NkDJ3KOM1XeGxqU9Oz9aOSFBceLELGIHwWTp; csm-hit=tb:298YFBB5FY62QC2SBRXY+b-298YFBB5FY62QC2SBRXY|1639464885586&t:1639464885586&adb:adblk_no'
            }
    search_query = str(data.loc[0,'brand']) + '-'+ str(data.loc[0,'name']).replace(' ','-')
    response = getAmazonSearch(search_query,headers)
    data_asin=['B01E096L0E']
    soup=BeautifulSoup(response.content)
    for a in soup.findAll("div",{'class':"sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item s-asin sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32"}):
        print(a)
        data_asin.append(a['data-asin'])

    # Attain the link according to asin
    link=[]
    response=Searchasin(data_asin[0])
    soup=BeautifulSoup(response.content)
    for b in soup.findAll("a",{'data-hook':"see-all-reviews-link-foot"}):
        link.append(b['href'])
    # Retrieve the comments
    reviews=[]
    for j in range(len(link)):
        for k in range(10):
            response=Searchreviews(link[j]+'&pageNumber='+str(k))
            soup=BeautifulSoup(response.content)
            for i in soup.findAll("span",{'data-hook':"review-body"}):
                reviews.append(i.text)
    for i in range(5):
        print(reviews[i])
    return reviews
reviews = spyder_review(data)
