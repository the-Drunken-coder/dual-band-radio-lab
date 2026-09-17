# Online primary-source evidence

Read 2026-09-17. These entries deliberately do not claim a successfully saved PDF when direct download failed.

- [TDK C3225X7R1E226M250AB product page](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3225X7R1E226M250AB): status Production, 22 uF +/-20%, 25 V X7R. Body 3.20 +/-0.40 by 2.50 +/-0.30, thickness 2.50 +/-0.30 mm; terminal width >=0.20 mm. Reflow. [Manufacturer characterization sheet, 2022-02-16](https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/c3225x7r1e226m250ab_220216.pdf) repeats dimensions and ratings. Web tool read the one-page PDF; shell download returned HTTP 403. No minimum capacitance under bias was inferred from an unviewed graph. POWER_BUDGET.md explicitly identifies its combined bias/aging allowance as an engineering bound to verify.
- [Phoenix 1757242 manufacturer PDF](https://www.phoenixcontact.com/en-us/products/pcb-header-mstba-25-2-g-508-1757242?type=pdf): 12 A, 5.08 mm pitch, 12.16 x 12 mm body, 8.57 installed height, 3.23 mm solder pins, 1 x 1 mm terminals, 1.4 mm finished hole. Manufacturer catalog names mating 1757019. Web tool read the PDF; shell download returned HTTP 403.
- [Accu SSCF-M3-25-A2](https://www.accu.co.uk/api/product-datasheet?id=642039): manufacturer own-brand full-thread M3 x 25, 0.5 mm pitch, A2 stainless, DIN912/ISO4762, head 5.5 mm diameter +0/-0.18 and 3 mm high +0/-0.14. Web search returned the product datasheet; shell download returned HTTP 403.
- [Accu HPN-M3-A2](https://www.accu.co.uk/hexagon-nuts/7888-HPN-M3-A2): M3, 0.5 mm pitch, 5.5 mm across flats +0/-0.18, 2.4 mm height +0/-0.25. No stock commitment is inferred from the page's dynamic purchase controls.

Murata GRM32ER61C226KE20L and GRM32ER61E226KE15L were considered, but subsequent lifecycle/discontinuation evidence and unavailable reference-sheet URLs led to selecting the currently listed TDK part instead. They are not substitute BOM entries.
