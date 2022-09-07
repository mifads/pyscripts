#!/usr/bin/env python3
"""
 This file sets EMEP codes, Iso3 and Iso2 (except where the EMEP
 model uses 3-letter Iso2 - e.g. ATL!)
"""
import collections
import os
import sys
import numpy as np

# 1) Country codes file: #EMEP   ISO3   ISO2  Name #1     ALB    AL    Albania

emepcodes=collections.OrderedDict() # stores iso2, iso3 etc.
iso2toIso3=collections.OrderedDict() # stores iso2, iso3 etc.
iso2toNum=dict()   # converts e.g. 'AL' to 1, etc.
emepcc2isos = dict()  # from '1' to 'ALB' or 'AL' or ..

#tnonum =dict()
country_list="""##################################################
# This file sets EMEP codes, Iso3 and Iso2 (except where the EMEP
# model uses 3-letter Iso2 - e.g. ATL!)
#EMEP   ISO3   ISO2  Name
1     ALB    AL    Albania
56    ARM    AM    Armenia
2     AUT    AT    Austria
69    AZE    AZ    Azerbaijan
3     BEL    BE    Belgium
4     BGR    BG    Bulgaria
50    BIH    BA    Bosnia_and_Herzegovina
39    BLR    BY    Belarus
24    CHE    CH    Switzerland
210   CHN    CN    China
55    CYP    CY    Cyprus
46    CZE    CZ    Czech_Republic
60    DEU    DE    Germany
6     DNK    DK    Denmark
22    ESP    ES    Spain
43    EST    EE    Estonia
7     FIN    FI    Finland
8     FRA    FR    France
27    GBR    GB    United_Kingdom
54    GEO    GE    Georgia
11    GRC    GR    Greece
49    HRV    HR    Croatia
12    HUN    HU    Hungary
14    IRL    IE    Ireland
13    ISL    IS    Iceland
15    ITA    IT    Italy
53    KAZ    KZ    Kazakhstan
45    LTU    LT    Lithuania
16    LUX    LU    Luxembourg
44    LVA    LV    Latvia
41    MDA    MD    Moldova_Republic_of
52    MKD    MK    Macedonia
57    MLT    MT    Malta
73    MNE    ME    Montenegro
17    NLD    NL    Netherlands
18    NOR    NO    Norway
19    POL    PL    Poland
20    PRT    PT    Portugal
21    ROU    RO    Romania
61    RUS    RU    Russian_Federation
72    SRB    RS    Serbia
47    SVK    SK    Slovakia
48    SVN    SI    Slovenia
23    SWE    SE    Sweden
25    TUR    TR    Turkey
40    UKR    UA    Ukraine
30    BAS    BS    Baltic_Sea
31    NOS    NS    North_Sea
32    ATL    AO    Atlantic_Ocean
33    MED    MS    Mediterranean_Sea
34    BLS    BS    Black_Sea
59    LI     LI    Lichtenstein
63    NOA    NOA   NorthAfrica
80    CAS    CAS   Caspian_Sea
601   GRL    GRL   Greenland
92    KZT    KZT   KazakhstanAll
93    RUE    RUE   RussianFedereationAll
94    UZB    UZT   Uzbekistan
95    TKM    TMT   Turkmenistan
96    AST    AST   AsiaAreasEmepDomain
373   KOS    KOS   Kosovo
237   EGY    EGYP  Egypt
250   IRN    IRAN  Iran_(Islamic_Republic_of)
214   ISR    ISRA  Israel
251   SAU    SAAR  Saudi_Arabia
110   IRQ    IRQ   Iraq
111   JOR    JOR   Jordan
112   KWT    KWT   Kuwait
113   LBN    LBN   Lebanon
114   LBY    LBY   Libya
115   MAR    MAR   Morocco
116   PSE    PSE   Palestine_State_of
117   SYR    SYR   Syrian_Arab_Republic
118   TUN    TUN   Tunisia 
119   DZA    DZA   Algeria
501   GRS    GRS   Greenland_Sea
502   BAR    BAR   Barents_Sea
503   NWS    NWS   Norwegian_Sea
504   ENC    ENC   English_Channel
505   IRC    IRC   Irish_Sea
506   KAR    KAR   Kara_Sea 
507   PSG    PSG   Persian_Gulf
999   EUR    EUR   European_sum_used_in_scripts
""" #############################################################

country_list_old="""##################################################
# This file sets EMEP codes, Iso3 and Iso2 (except where the EMEP
# model uses 3-letter Iso2 - e.g. ATL!)
#EMEP   ISO3   ISO2  Name
1     ALB    AL    Albania
56    ARM    AM    Armenia
2     AUT    AT    Austria
69    AZE    AZ    Azerbaijan
3     BEL    BE    Belgium
4     BGR    BG    Bulgaria
50    BIH    BA    Bosnia_and_Herzegovina
39    BLR    BY    Belarus
24    CHE    CH    Switzerland
55    CYP    CY    Cyprus
46    CZE    CZ    Czech_Republic
60    DEU    DE    Germany
6     DNK    DK    Denmark
22    ESP    ES    Spain
43    EST    EE    Estonia
7     FIN    FI    Finland
8     FRA    FR    France
27    GBR    GB    United_Kingdom
54    GEO    GE    Georgia
11    GRC    GR    Greece
49    HRV    HR    Croatia
12    HUN    HU    Hungary
14    IRL    IE    Ireland
13    ISL    IS    Iceland
15    ITA    IT    Italy
53    KAZ    KZ    Kazakhstan
68    KGZ    KG    Kyrgyzstan
45    LTU    LT    Lithuania
16    LUX    LU    Luxembourg
44    LVA    LV    Latvia
41    MDA    MD    Moldova_Republic_of
52    MKD    MK    Macedonia
57    MLT    MT    Malta
17    NLD    NL    Netherlands
18    NOR    NO    Norway
19    POL    PL    Poland
20    PRT    PT    Portugal
21    ROU    RO    Romania
61    RUS    RU    Russian_Federation
47    SVK    SK    Slovakia
48    SVN    SI    Slovenia
23    SWE    SE    Sweden
25    TUR    TR    Turkey
40    UKR    UA    Ukraine
51    YUG    CS    Serbia_and_Montenegro		
30    BAS    BAS   Baltic_Sea
31    NOS    NOS   North_Sea
32    ATL    ATL   Atlantic_Ocean
70    ATX    ATX   Rest_of_Atlantic_Ocean
33    MED    MED   Mediterranean_Sea
34    BLS    BLS   Black_Sea
58    ASI    ASI   Rest_of_Asia
350   INT    INTSHIPS    International_shipping
501   GRS    GRS   Greenland_Sea
502   BAR    BAR   Barents_Sea
503   NWS    NWS   Norwegian_Sea
504   ENC    ENC   English_Channel
505   IRC    IRC   Irish_Sea
506   KAR    KAR   Kara_Sea
507   PSG    PSG   Persian_Gulf
73    MNE   MNE  Montenegro
80    CAS   CAS  Caspian_Sea_in_the_original_EMEP_domain
237   EGY   EGY  Egypt
214   ISR   ISRA  Israel
250   IRN   IRN  Iran
251   SAU   SAU  Saudi_Arabia
373   KOS   KOS  Kosovo
110   IRQ   IRQ  Iraq
111   JOR   JOR  Jordan
112   KWT   KWT  Kuwait
113   LBN   LBN  Libanon
114   LBY   LBY  Libya
115   MAR   MAR  Morocco
116   PSE   PSE  Palestine_State_of
117   SYR   SYR  Syrian_Arab_Republic
118   TUN   TUN  Tunisia
119   DZA   DZA  Algeria
601   GRL   GRL  Greenland
""" #############################################################

def get_emepcodes():

   for ncc, line in list(enumerate(country_list.splitlines())):
      if line == '': continue    # header
      if line.startswith('#'): continue    # header
      cc, iso3, iso2, name = line.split()
      emepcodes[iso3] = dict( cc = int(cc), iso2=iso2, iso3=iso3, name=name )

      iso2toIso3[iso2] = iso3
      iso2toNum[iso2]  = int(cc)
      emepcc2isos[cc] = dict( iso2=iso2, iso3=iso3, name=name )
#      tnonum[iso3] = ncc   # eg GBR -> 27
   return emepcodes  # , iso2toIso3

def getIso3(iso2):
    """ Uses dict from above to convert emep iso2 codes to iso3 for MACC """
    return iso2toIso3[iso2]

def getIso2toNum(iso2):
    """ Uses dict from above to convert emep iso2 codes to iso3 for MACC """
    return iso2toNum[iso2]

if __name__ == '__main__':

    c=get_emepcodes()
    maxnum = 0
    for iso3 in c.keys():
       cnum = c[iso3]['cc']
       if cnum>maxnum: maxnum = cnum
       print( iso3, cnum, maxnum)
#        print( land['cc'] )
        #print( land['cc'] )
