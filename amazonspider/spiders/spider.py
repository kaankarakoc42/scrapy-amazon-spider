import scrapy
from ..items import AmazonspiderItem

class QuotesSpider(scrapy.Spider):
    name = "quotes" #örümceğin ismi bura yüzünden scrapy crawl quotes yazıyoruz
    
    start_urls = ["https://www.amazon.com.tr/s?k=GROCERY&i=grocery&page=1"] #ilk istek atılacak url
    base_page = "https://www.amazon.com.tr/s?k=GROCERY&i=grocery&page={0}" #sayfa sayısını artırmak için tutuyoruz
    item_url = "https://www.amazon.com.tr{0}"#burayada item url koymak için tutuyoruz
    page_count = 1 #başlangıç ve devam eden sayfa sayısı
    pageOritem = "getitem" #şu anki yapılan işlem
    items = [] #alınan itemların url leri 
    item_count = 1 #sayfadaki ürünün sırası ör 1.sayfa 1.ürün
    
    page_limit = 6 # durdurulacak sayfa

    
    def setstate(self,state):
        self.pageOritem = state

              
    def itempage(self,response):
        item_data = {
                "title" : str(response.css("h1#title span::text").get()).replace("\n",""),
                "brand" : str(response.css("a#bylineInfo::text").get()).replace("\n",""),
                "price" : str(response.css("span#price_inside_buybox::text").get()).replace("\n",""),
                "desc"  : {x:y for x,y in tuple(zip([str(i).replace("\n","") for i in response.css("table#productDetails_techSpec_section_1 tr th::text").getall()],
                                                    [str(i).replace("\n","") for i in response.css("table#productDetails_techSpec_section_1 tr td::text").getall()]))
                },
                "bullets": [str(i).replace("\n","") for i in response.css("div#feature-bullets ul li span::text").getall()],
                "stars":response.css('span[data-hook="rating-out-of-text"]::text').get()  
        }#bilgileri sözlük şekline getirdik
        yield AmazonspiderItem(item_data)#dışa aktardık
        url=self.item_url.format(self.items[self.item_count])
        self.item_count+=1
        if self.item_count==23: #eğer 23.üründeysek sonraki sayfaya geç değilsek devam
           self.setstate("nextpage")
           self.item_count=1
        yield response.follow(url,callback = self.parse, dont_filter=True)    
    
    def getitem(self,response):
        self.items = [] 
        for item_count in range(1,24):
               self.items.append(response.xpath(f'//*[@id="search"]/div[1]/div/div[1]/div/span[3]/div[2]/div[{item_count}]/div/span/div/div').css("a::attr(href)").get())
        url=self.item_url.format(self.items[0])
        self.setstate("itempage")
        yield response.follow(url,callback = self.parse)
        

    def nextpage(self,response):
        if self.page_count<self.page_limit:
            next_page = self.base_page.format(self.page_count)
            self.page_count +=1
            self.setstate("getitem")
            yield response.follow(next_page,callback = self.parse)         
    
    def parse(self, response):
        #üç tane aşama var sırasıyla biri bittiğinda onu çalıştırıyor
        yield from {
        "itempage":self.itempage,
        "getitem":self.getitem,
        "nextpage":self.nextpage
        }.get(self.pageOritem)(response)
   


