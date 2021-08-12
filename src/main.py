import pandas as pd
from selenium import webdriver

YEAR = 2020
URL = f"https://www.shanghairanking.com/rankings/arwu/{YEAR}"


def main():

    df = []
    country_list = []

    with webdriver.Chrome() as driver:
        driver.get(URL)
        for _ in range(50):

            tbl = pd.read_html(
                driver.find_element_by_class_name("rk-table").get_attribute("outerHTML")
            )[0]
            countries = [
                e.get_attribute("style")
                for e in driver.find_elements_by_class_name("region-img")
            ]
            assert len(tbl) == len(countries)

            country_list += countries
            df.append(tbl)

            driver.find_element_by_class_name("anticon-right").click()

    df = pd.concat(df)
    df["country"] = country_list
    df = df.drop_duplicates()

    df["country_iso_code"] = df.country.str.upper().str.extract("([A-Z]{2})\.PNG")

    iso = pd.read_csv(
        "https://raw.githubusercontent.com/owid/covid-19-data/master/scripts/input/iso/iso.csv"
    )

    df = (
        pd.merge(df, iso, left_on="country_iso_code", right_on="alpha-2", how="left")
        .drop(
            columns=[
                "Unnamed: 2",
                "Unnamed: 5",
                "country",
                "alpha-2",
                "alpha-3",
                "iso_code",
            ]
        )
        .rename(
            columns={
                "Institution": "institution",
                "Total Score": "total_score",
                "World Rank": "world_rank",
                "National/Regional Rank": "national_rank",
                "location": "country",
            }
        )
    )

    df["year"] = YEAR

    df.to_csv(f"output/shanghai_{YEAR}.csv", index=False)


if __name__ == "__main__":
    main()
