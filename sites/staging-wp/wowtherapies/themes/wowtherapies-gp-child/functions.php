<?php
/**
 * WOW Therapies — GeneratePress child theme.
 *
 * @package wowtherapies-gp-child
 */

defined( 'ABSPATH' ) || exit;

/**
 * Enqueue parent and child styles.
 */
function wowtherapies_enqueue_styles() {
	wp_enqueue_style(
		'generatepress-parent',
		get_template_directory_uri() . '/style.css',
		array(),
		wp_get_theme( 'generatepress' )->get( 'Version' )
	);
	wp_enqueue_style(
		'wowtherapies-child',
		get_stylesheet_uri(),
		array( 'generatepress-parent' ),
		wp_get_theme()->get( 'Version' )
	);
}
add_action( 'wp_enqueue_scripts', 'wowtherapies_enqueue_styles', 15 );

/**
 * Register a primary menu location label (GP uses menu-1 by default).
 */
function wowtherapies_setup() {
	register_nav_menus(
		array(
			'primary' => __( 'Primary', 'wowtherapies-gp-child' ),
		)
	);
}
add_action( 'after_setup_theme', 'wowtherapies_setup' );

/**
 * Educational disclaimer in footer.
 */
function wowtherapies_footer_disclaimer() {
	?>
	<div class="wt-disclaimer" role="note" aria-label="<?php esc_attr_e( 'Educational disclaimer', 'wowtherapies-gp-child' ); ?>">
		<p>
			<strong><?php esc_html_e( 'Educational information only.', 'wowtherapies-gp-child' ); ?></strong>
			<?php esc_html_e( 'Content on this site is for general education and does not replace evaluation or treatment by a licensed speech-language pathologist or other qualified provider. If you have concerns about speech, language, voice, or swallowing, request an evaluation.', 'wowtherapies-gp-child' ); ?>
		</p>
	</div>
	<?php
}
add_action( 'generate_after_footer_content', 'wowtherapies_footer_disclaimer', 8 );

/**
 * Optional body class for front-page styling.
 *
 * @param array $classes Body classes.
 * @return array
 */
function wowtherapies_body_classes( $classes ) {
	if ( is_front_page() ) {
		$classes[] = 'wt-front-page';
	}
	return $classes;
}
add_filter( 'body_class', 'wowtherapies_body_classes' );
