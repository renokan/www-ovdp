
dict_q = {}

dict_q['years'] = "SELECT DISTINCT CAST(strftime('%Y', date_in) as INTEGER) as year \
                        FROM auctions \
                        WHERE year > {} \
                        ORDER BY year ASC;"

dict_q['auctions'] = "SELECT * FROM auctions \
                        WHERE CAST(strftime('%Y', date_in) as INTEGER) > {} \
                        ORDER BY date_in DESC, auct_num DESC;"

dict_q['auct_year'] = "SELECT * FROM auctions \
                        WHERE CAST(strftime('%Y', date_in) as INTEGER) = {} \
                        ORDER BY date_in DESC, auct_num DESC;"
