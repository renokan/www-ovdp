
queries = {}

queries['years'] = "SELECT DISTINCT CAST(strftime('%Y', date_in) as INTEGER) as year \
                                FROM auctions \
                                WHERE year > {} \
                                ORDER BY year ASC;"

queries['auctions'] = "SELECT * FROM auctions \
                                WHERE CAST(strftime('%Y', date_in) as INTEGER) > {} \
                                ORDER BY date_in DESC, auct_num DESC;"

queries['auct_year'] = "SELECT * FROM auctions \
                                 WHERE CAST(strftime('%Y', date_in) as INTEGER) = {} \
                                 ORDER BY date_in DESC, auct_num DESC;"
