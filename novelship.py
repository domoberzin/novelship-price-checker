import requests
from dhooks import Webhook, Embed
from copy import deepcopy


def search_novel(search_query):
    search_query=(str(search_query)).replace(" ","%20")
    search_url = "https://novelship.com/api/products/search?where[search]=" +search_query+ "&where[active:eq]=true&page[number]=0&page[size]=20"
    headers_dict = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
    hook = Webhook("insert-webhook-here")





    search = requests.get(search_url,headers=headers_dict).json()
    if search["results"] != []:
        print(search)
        pid = str(search["results"][0]["objectID"])
        pid = pid[0:5] #probably need to fix this
        name = search["results"][0]["name"]
        name_slug = search["results"][0]["name_slug"]
        a = requests.get("https://novelship.com/api/products/slug/"+ name_slug + "?where[active:eq]=true",headers=headers_dict).json()
        print(a.keys())
        size_list_bids = a["sizes"]
        size_list_asks = deepcopy(size_list_bids)
        sku = ""
        if search["results"][0]["sku"] != None:
            sku = search["results"][0]["sku"]
        else:
            sku = "(SKU not available)"
        image_url = search["results"][0]["image"]

        found_url =  "https://novelship.com/api/products/" + pid +  "/offer-lists?where[active:eq]=true&modifier[c]=3&page[number]=0&page[size]=1000"
        found = requests.get(found_url,headers=headers_dict).json()
        print(found)
        buying_price_list = []
        selling_price_list= []
        for i in range(len(found["results"])):
            try:
                if found["results"][i]["type"] == "buying":
                    price = found["results"][i]["price"]
                    buying_price_list.append(((str(found["results"][i]["size"])),int(f"{price:.0f}"),str((f"{(price*0.884- 6.80 - 0.70):.0f}")),(float(found["results"][i]["size"][3:]))))
                if found["results"][i]["type"] == "selling":
                    price2= found["results"][i]["price"]
                    selling_price_list.append(((str(found["results"][i]["size"])),int(f"{price2:.0f}"),str((f"{(price2*0.884- 6.80 - 0.70):.0f}")),(float(found["results"][i]["size"][3:]))))
                sorted_bids = sorted(buying_price_list,key =lambda x:x[3])
                sorted_asks2 = sorted(selling_price_list,key =lambda x:x[3])
            except ValueError:
                if found["results"][i]["type"] == "buying":
                    price = found["results"][i]["price"]
                    buying_price_list.append(((str(found["results"][i]["size"])),int(f"{price:.0f}"),str((f"{(price*0.884- 6.80 - 0.70):.0f}"))))
                if found["results"][i]["type"] == "selling":
                    price2= found["results"][i]["price"]
                    selling_price_list.append(((str(found["results"][i]["size"])),int(f"{price2:.0f}"),str((f"{(price2*0.884- 6.80 - 0.70):.0f}"))))
                sorted_bids = sorted(buying_price_list,key =lambda x:x[1])
                sorted_asks2 = sorted(selling_price_list,key =lambda x:x[1])



        for i in range(len(sorted_bids)-1,-1,-1):
            try:
                if sorted_bids[i][0] == sorted_bids[i+1][0]:
                    if sorted_bids[i][1] > sorted_bids[i+1][1]:
                        sorted_bids.remove[(i+1)]
                    elif sorted_bids[i][1] < sorted_bids[i+1][1]:
                        sorted_bids.remove(sorted_bids[i])
            except:
                pass

        for i in sorted_bids:
            if i[0] in size_list_bids:
                position_of_size = size_list_bids.index(i[0])
                size_list_bids[position_of_size] = (i[0],i[1],i[2])

        for i in range(len(sorted_asks2)-1,-1,-1):
            try:
                if sorted_asks2[i][0] == sorted_asks2[i+1][0]:
                    if sorted_asks2[i][1] < sorted_asks2[i+1][1]:
                        sorted_asks2.remove[(i+1)]
                    elif sorted_asks2[i][1] > sorted_asks2[i+1][1]:
                        sorted_asks2.remove(sorted_asks2[i])
            except:
                pass

        for i in sorted_asks2:
            if i[0] in size_list_asks:
                position_of_size = size_list_asks.index(i[0])
                size_list_asks[position_of_size] = (i[0],i[1],i[2])
        print(size_list_asks)
        print(size_list_bids)
        final_bids_list = []
        final_asks_list = []
        for i in range(len(size_list_asks)):
            if type(size_list_asks[i]) == tuple:
                size_list_asks[i] = "{} : {} : {}".format(size_list_asks[i][0],size_list_asks[i][1],size_list_asks[i][2])
                final_asks_list.append(size_list_asks[i])
            else:
                final_asks_list.append("{} : No asks".format(size_list_asks[i]))

        for i in range(len(size_list_bids)):
            if type(size_list_bids[i]) == tuple:
                size_list_bids[i] = "{} : {} : {}".format(size_list_bids[i][0],size_list_bids[i][1],size_list_bids[i][2])
                final_bids_list.append(size_list_bids[i])
            else:
                final_bids_list.append("{} : No bids".format(size_list_bids[i]))


        final_asks = "\n".join(final_asks_list)
        final_bids = "\n".join(final_bids_list)

        try:
            embed = Embed(
                description=name + " " + sku,
                color=0x5CDBF0,
                timestamp='now'  # sets the timestamp to current time

            )


            embed.set_author(name='Novelship Price Checker (At 8.6% Seller Fee)')
            embed.set_image(image_url)
            embed.add_field(name='Lowest Ask : Takeback', value=final_asks)
            embed.add_field(name='Highest Bid : Takeback', value=final_bids)
            hook.send(embed=embed)
            pass
        except requests.exceptions.HTTPError as err:
            embed = Embed(
                description="Request error",
                color=0x5CDBF0,
                timestamp='now'  # sets the timestamp to current time

            )
            hook.send(embed=embed)
    else:
        embed = Embed(
            description="Search invalid",
            color=0x5CDBF0,
            timestamp='now'  # sets the timestamp to current time

        )
        hook.send(embed=embed)

if __name__ == "__main__":
    while True:
        search_novel(input("Please input"))
