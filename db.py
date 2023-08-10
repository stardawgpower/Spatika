import pyodbc

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = 'hunnarvi.database.windows.net' 
database = 'kreisonlinebilling-prod' 
username = 'suadmin' 
password = 'WKsR14msuZ7' 

# ENCRYPT defaults to yes starting in ODBC Driver 18. It's good to always specify ENCRYPT=yes on the client side to avoid MITM attacks.
# cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password)
# cursor = cnxn.cursor()

class ItemDatabse:
    
    def __init__(self):
        self.conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password)
        self.cursor = self.conn.cursor()
        
    def get_counts(self):
        result = []
        query = """
                SELECT
                COUNT(CASE WHEN DATEDIFF(day, Workflow_Assign_Date, GETDATE()) <= 7 THEN 1 ELSE NULL END) AS '<=7',
                COUNT(CASE WHEN DATEDIFF(day, Workflow_Assign_Date, GETDATE()) BETWEEN 8 AND 15 THEN 1 ELSE NULL END) AS '8-15',
                COUNT(CASE WHEN DATEDIFF(day, Workflow_Assign_Date, GETDATE()) BETWEEN 16 AND 30 THEN 1 ELSE NULL END) AS '16-30',
                COUNT(CASE WHEN DATEDIFF(day, Workflow_Assign_Date, GETDATE()) BETWEEN 31 AND 60 THEN 1 ELSE NULL END) AS '31-60',
                COUNT(CASE WHEN DATEDIFF(day, Workflow_Assign_Date, GETDATE()) >= 61 THEN 1 ELSE NULL END) AS '>60'
                
                FROM trx_ra_bill A
                LEFT JOIN trx_Payments B ON B.ref_ra_bill_id = A.ra_bill_id
                LEFT JOIN trx_Workflow C ON C.ref_ra_bill_id = A.ra_bill_id

                WHERE C.Ref_Workflow_Role_Id = 3
                AND A.ra_bill_id NOT IN (SELECT ref_ra_bill_id FROM trx_Payments
                
                GROUP BY ref_ra_bill_id)
                """
        self.cursor.execute(query)
        for row in self.cursor.fetchall():
            item_dict = {}
            item_dict["Count <=7 days"] = row[0]
            item_dict["Count 8-15 days"] = row[1]
            item_dict["Count 16-30 days"] = row[2]
            item_dict["Count 31-60 days"] = row[3]
            item_dict["Count >60 days"] = row[4]
            result.append(item_dict)
        return result

    def get_monthly_amounts_for_in_progress_bills(self):
        query = """
                SELECT
                YEAR(DATEADD(month, DATEDIFF(month, 31, C.transaction_date), 0)) AS year,
                MONTH(DATEADD(month, DATEDIFF(month, 31, C.transaction_date), 0)) AS month,
                SUM(C.ra_bill_amt) AS total_amount

                FROM trx_RA_Bill A
                LEFT JOIN trx_Workflow B ON B.ref_ra_bill_id = A.ra_bill_id
                INNER JOIN trx_Payments C ON C.ref_ra_bill_id = A.RA_Bill_Id
                LEFT JOIN trx_BrNo D ON D.RA_Bill_No = A.RA_Bill_Id
                LEFT JOIN mst_Project E ON E.Project_Id = A.Ref_Project_Id
                LEFT JOIN mst_Package F ON F.Package_Id = A.Ref_Package_Id

                WHERE
                Workflow_Comp_Flag = 1 AND Workflow_Comp_Date IS NOT NULL AND Ref_Workflow_Role_Id = 18
                AND C.ra_bill_trans_id in (SELECT max(ra_bill_trans_id) FROM trx_Payments group by ref_ra_bill_id)

                GROUP BY
                YEAR(DATEADD(month, DATEDIFF(month, 31, C.transaction_date), 0)),
                MONTH(DATEADD(month, DATEDIFF(month, 31, C.transaction_date), 0))

                ORDER BY 
                year, month
                """
        self.cursor.execute(query)
    
        years = []
        months = []
        amounts = []
        for row in self.cursor.fetchall():
            years.append(row[0])
            months.append(row[1])
            amounts.append(row[2])
    
        # close the connection and return the lists
        # self.conn.close()
        return years, months, amounts

    def get_monthly_amounts_for_total_approved_bills(self):
    
        query = """
                SELECT
	            YEAR(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Comp_Date), 0)) AS year,
                MONTH(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Comp_Date), 0)) AS month,
	            SUM(C.ra_bill_amt) AS total_amount
            
                FROM trx_RA_Bill A
	            LEFT JOIN trx_Workflow B ON B.ref_ra_bill_id = A.ra_bill_id
	            INNER JOIN trx_Payments C ON C.ref_ra_bill_id = A.RA_Bill_Id
	            LEFT JOIN trx_BrNo D ON D.RA_Bill_No = A.RA_Bill_Id
            	LEFT JOIN mst_Project E ON E.Project_Id = A.Ref_Project_Id
            	LEFT JOIN mst_Package F ON F.Package_Id = A.Ref_Package_Id

                WHERE Workflow_Comp_Flag = 1 
                AND Workflow_Comp_Date IS NOT NULL 
                AND Ref_Workflow_Role_Id = 18
                AND C.ra_bill_trans_id in (SELECT max(ra_bill_trans_id) FROM trx_Payments group by ref_ra_bill_id)

                GROUP BY
                YEAR(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Comp_Date), 0)),
                MONTH(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Comp_Date), 0))

                ORDER BY year, month
                """
        self.cursor.execute(query)
    
        year = []
        months = []
        amounts = []
        for row in self.cursor.fetchall():
            year.append(row[0])
            months.append(row[1])
            amounts.append(row[2])
    
        # close the connection and return the lists
        # self.conn.close()
        return year, months, amounts
    
    def get_monthly_amounts_for_RA_bills_raised(self):
    
        query = """
                SELECT			 
                YEAR(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Assign_Date), 0)) AS year,
                MONTH(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Assign_Date), 0)) AS month,
                SUM(A.RA_Bill_Amt) AS total_amount

                FROM trx_RA_Bill A
                LEFT JOIN trx_Workflow B ON B.Ref_RA_Bill_Id = A.RA_Bill_Id
                LEFT JOIN mst_Project C ON C.project_id = A.Ref_Project_Id
                LEFT JOIN mst_Package D ON D.package_Id = A.Ref_Package_Id
                LEFT JOIN mst_Contractor E ON E.Contractor_Id = A.Contractor_Id
                LEFT JOIN trx_BrNo F ON F.RA_Bill_No = A.RA_Bill_Id

                WHERE B.Ref_Workflow_Role_Id = 3 

                AND C.Project_Active = 1 
                AND D.Package_Active = 1 
                AND E.Contractor_Active = 1

                GROUP BY
                YEAR(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Assign_Date), 0)),
                MONTH(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Assign_Date), 0))

                ORDER BY year, month
                """
        self.cursor.execute(query)
    
        years = []
        months = []
        amounts = []
        for row in self.cursor.fetchall():
            years.append(row[0])
            months.append(row[1])
            amounts.append(row[2])
        
        # close the connection and return the lists
        # self.conn.close()
        return years, months, amounts
    
    def get_monthly_amounts_for_total_amount_paid(self):
        query = """
                SELECT			
	            YEAR(DATEADD(month, DATEDIFF(month, 31, C.transaction_date),0)) as year,
	            month(DATEADD(month, DATEDIFF(month, 31, C.transaction_date),0)) as month,
                SUM(C.ra_bill_amt) as TOTAL_AMOUNT

                FROM trx_RA_Bill A
                LEFT JOIN trx_Workflow B ON B.ref_ra_bill_id = A.ra_bill_id
                INNER JOIN trx_Payments C ON C.ref_ra_bill_id = A.RA_Bill_Id
                LEFT JOIN trx_BrNo D ON D.RA_Bill_No = A.RA_Bill_Id
                LEFT JOIN mst_Project E ON E.Project_Id = A.Ref_Project_Id
                LEFT JOIN mst_Package F ON F.Package_Id = A.Ref_Package_Id

                WHERE				
		        Workflow_Comp_Flag = 1 
                AND Workflow_Comp_Date IS NOT NULL 
                AND Ref_Workflow_Role_Id = 18
                AND C.ra_bill_trans_id in (SELECT max(ra_bill_trans_id) FROM trx_Payments group by ref_ra_bill_id)
            
                GROUP BY 
                YEAR(DATEADD(month, DATEDIFF(month, 31, C.transaction_date),0)),
                MONTH(DATEADD(month, DATEDIFF(month, 31, C.transaction_date),0))

                ORDER BY year, month
                """
        self.cursor.execute(query)
    
        years = []
        months = []
        amounts = []
        for row in self.cursor.fetchall():
            years.append(row[0])
            months.append(row[1])
            amounts.append(row[2])
        
        # close the connection and return the lists
        # self.conn.close()
        return years, months, amounts
    
    def get_monthly_amounts_for_contractor_claimed_amount(self):
        query = """
                SELECT
                YEAR(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Assign_Date),0)) as year,
                month(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Assign_Date),0)) as month,
                SUM(A.RA_Bill_Amt) as TOTAL_AMOUNT

                FROM trx_RA_Bill A
                LEFT JOIN trx_Workflow B ON B.Ref_RA_Bill_Id = A.RA_Bill_Id
                LEFT JOIN mst_Project C ON C.project_id = A.Ref_Project_Id
                LEFT JOIN mst_Package D ON D.package_Id = A.Ref_Package_Id
                LEFT JOIN mst_Contractor E ON E.Contractor_Id = A.Contractor_Id
                LEFT JOIN trx_BrNo F ON F.RA_Bill_No = A.RA_Bill_Id

                WHERE B.Ref_Workflow_Role_Id = 3 

                AND C.Project_Active = 1 
                AND D.Package_Active = 1 
                AND E.Contractor_Active = 1

                GROUP BY 
                YEAR(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Assign_Date),0)),
	            MONTH(DATEADD(month, DATEDIFF(month, 31, B.Workflow_Assign_Date),0))
            
                ORDER BY year, month                
                """
        self.cursor.execute(query)
    
        years = []
        months = []
        amounts = []
        for row in self.cursor.fetchall():
            years.append(row[0])
            months.append(row[1])
            amounts.append(row[2])
        
        # close the connection and return the lists
        # self.conn.close()
        return years, months, amounts
    
    def get_unique_contractor_id(self):
        query = """
                SELECT 
                DISTINCT Contractor_Id,Contractor_name
                FROM mst_Contractor
                """
        self.cursor.execute(query)
        contractor_id = []
        contractor_name = []
        for row in self.cursor.fetchall():
            contractor_id.append(row[0])
            contractor_name.append(row[1])
        
        # close the connection and return the lists
        # self.conn.close()
        return contractor_id, contractor_name

