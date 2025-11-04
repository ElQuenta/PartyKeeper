from principalTool import search_page


def main():
	print('Buscando curio: Giant Oyster en darkestdungeon.wiki.gg')
	try:
		res = search_page('Giant Oyster')
	except Exception as e:
		print('Error al consultar la wiki:', e)
		return

	print('\nURL encontrada:', res.get('url'))
	print('\n--- Extracto (primeros 2000 chars) ---\n')
	text = res.get('text', '')
	if not text:
		print('No se extrajo texto. La página puede no existir o el formato cambió.')
	else:
		print(text[:2000])


if __name__ == '__main__':
	main()

