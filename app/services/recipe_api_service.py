import requests

class RecipeAPIError(Exception):
    pass

class HealthyRecipeService:
    BASE_URL = "https://www.themealdb.com/api/json/v1/1/search.php"

    @staticmethod
    def search_recipes(query="", limit=6):
        params = {"s": query}
        try:
            response = requests.get(HealthyRecipeService.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise RecipeAPIError("No fue posible conectarse con el servicio de recetas.") from exc
        except ValueError as exc:
            raise RecipeAPIError("La API devolvio una respuesta JSON invalida.") from exc

        meals = data.get("meals") or []
        results = []
        for meal in meals[:limit]:
            results.append({
                "name": meal.get("strMeal"),
                "category": meal.get("strCategory"),
                "area": meal.get("strArea"),
                "instructions": meal.get("strInstructions"),
                "image": meal.get("strMealThumb"),
                "tags": meal.get("strTags"),
                "source": meal.get("strSource"),
            })
        return results
